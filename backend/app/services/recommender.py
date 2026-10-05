"""
Hybrid recommendation engine.

Design (from the project proposal / design phase):
  * SWITCHING hybrid - collaborative filtering (item-based CF, scikit-learn)
    when the user has enough logging history, otherwise a content-based
    fallback (this solves the cold-start problem).
  * GOAL-CONSTRAINED - candidates are filtered by the user's fitness goal
    BEFORE ranking, so recommendations serve health goals, not just taste.
  * EXPLAINABLE - every recommendation carries a human-readable `reason`.

Foods are represented by their nutrition profile (calories and macro
density); exercises by MET value and category.
"""
import math
from datetime import date, datetime, timedelta

import numpy as np

from app import db
from app.models import Exercise, Food, MealLog, Recommendation, WorkoutLog
from app.utils.calories import met_calories

# ---------------------------------------------------------------------------
# Feature engineering
# ---------------------------------------------------------------------------

def _food_features(food):
    """Nutrition profile per serving -> 4-d vector [cal, protein, carbs, fat].

    Macros are expressed as density per 100 kcal so the similarity measures
    *quality* of the food rather than portion size.
    """
    cal = max(food.calories, 1.0)
    return np.array([
        min(food.calories / 500.0, 1.0),   # energy level, capped
        min(food.protein / cal * 10, 1.0), # protein density
        min(food.carbs / cal * 10, 1.0),   # carb density
        min(food.fat / cal * 10, 1.0),     # fat density
    ])


# Ideal nutrition vectors per goal (then normalized -> cosine similarity).
_FOOD_GOAL_VECTORS = {
    "lose":     np.array([0.2, 1.0, 0.4, 0.1]),  # low energy, high protein
    "gain":     np.array([0.8, 0.8, 0.7, 0.3]),  # energy-dense, high protein
    "maintain": np.array([0.5, 0.6, 0.5, 0.3]),  # balanced
}


def _exercise_features(exercise):
    """Exercise -> 5-d vector [MET level, cardio, strength, flexibility, sports]."""
    met = min(exercise.met_value / 12.0, 1.0)
    one_hot = {
        "cardio":      [1.0, 0.0, 0.0, 0.0],
        "strength":    [0.0, 1.0, 0.0, 0.0],
        "flexibility": [0.0, 0.0, 1.0, 0.0],
        "sports":      [0.0, 0.0, 0.0, 1.0],
    }.get(exercise.category, [0.0, 0.0, 0.0, 0.0])
    return np.array([met, *one_hot])


# Ideal exercise vectors per goal.
_EXERCISE_GOAL_VECTORS = {
    "lose":     np.array([0.9, 1.0, 0.1, 0.2, 0.4]),  # cardio, high burn
    "gain":     np.array([0.3, 0.1, 1.0, 0.2, 0.3]),  # strength focus
    "maintain": np.array([0.5, 0.6, 0.5, 0.4, 0.5]),  # mixed
}


# ---------------------------------------------------------------------------
# Similarity helpers (scikit-learn with a pure-numpy fallback)
# ---------------------------------------------------------------------------

def _cosine_similarity_matrix(rows):
    """Row-normalized cosine similarity between every pair of vectors."""
    matrix = np.asarray(rows, dtype=float)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    matrix = matrix / norms
    return matrix @ matrix.T


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

class RecommendationEngine:
    """Switching hybrid recommender: CF when history exists, else content-based."""

    def __init__(self, cf_min_meal_logs=5, cf_min_workout_logs=3):
        self.cf_min_meal_logs = cf_min_meal_logs
        self.cf_min_workout_logs = cf_min_workout_logs

    # ------------------------------------------------------------------ meals

    def recommend_meals(self, user, limit=5):
        """Return up to `limit` meal recommendations for `user`.

        Each item: {item_id, name, score, reason, calories, protein, ...}
        """
        goal = user.active_goal
        meal_count = user.meal_logs.count()
        if meal_count >= self.cf_min_meal_logs:
            strategy = "cf"
            results = self._cf_meals(user, goal, limit)
        else:
            strategy = "cb"  # content-based fallback (cold start)
            results = self._content_based_meals(user, goal, limit)

        # Record every generated recommendation (explainability + history).
        today = datetime.utcnow()
        for r in results:
            rec = Recommendation(
                user_id=user.id, rec_type="meal", item_id=r["item_id"],
                score=r["score"], reason=r["reason"], created_at=today,
            )
            db.session.add(rec)
        return results, strategy

    def _content_based_meals(self, user, goal, limit):
        goal_type = goal.goal_type if goal else "maintain"
        target = _FOOD_GOAL_VECTORS[goal_type]
        foods = Food.query.all()
        candidates = [
            f for f in foods
            if not self._logged_today(user, f.id)
            and not self._recommended_recently(user, f.id, "meal")
        ]
        if len(candidates) < limit:  # relax: only exclude recent duplicates
            candidates = [f for f in foods if not self._recommended_recently(user, f.id, "meal")]
        if not candidates:
            candidates = foods

        scored = self._rank_by_similarity(candidates, _food_features, target)
        return self._build_meal_results(scored, user, goal, limit)

    def _cf_meals(self, user, goal, limit):
        """Item-based CF over the global user x food matrix (quantity as implicit rating)."""
        goal_type = goal.goal_type if goal else "maintain"
        rows = db.session.query(MealLog.user_id, MealLog.food_id,
                                db.func.sum(MealLog.quantity)).group_by(
            MealLog.user_id, MealLog.food_id).all()
        users = sorted({r[0] for r in rows})
        foods = sorted({r[1] for r in rows})
        if len(users) < 2 or len(foods) < 2:
            return self._content_based_meals(user, goal, limit)  # CF needs data

        u_index = {u: i for i, u in enumerate(users)}
        f_index = {f: i for i, f in enumerate(foods)}
        matrix = np.zeros((len(users), len(foods)))
        for uid, fid, qty in rows:
            matrix[u_index[uid], f_index[fid]] = math.log1p(qty)  # dampen heavy users

        # Item-item similarity (food x food).
        sim = _cosine_similarity_matrix(matrix.T)

        # The user's own implicit ratings.
        my_ratings = np.zeros(len(foods))
        for uid, fid, qty in rows:
            if uid == user.id:
                my_ratings[f_index[fid]] = math.log1p(qty)
        logged_by_me = {f for f in foods if my_ratings[f_index[f]] > 0}

        # Predict:  r(u, i) = sum_j sim(i, j) * r(u, j) / sum_j |sim(i, j)|
        scored = []
        goal_target = _FOOD_GOAL_VECTORS[goal_type]
        for candidate_id in foods:
            if candidate_id in logged_by_me:
                continue  # never re-recommend foods the user already knows
            if self._recommended_recently(user, candidate_id, "meal"):
                continue
            ci = f_index[candidate_id]
            denom, num = 0.0, 0.0
            best_source = None
            for j in range(len(foods)):
                w = sim[ci, j]
                if w <= 0 or my_ratings[j] <= 0:
                    continue
                num += w * my_ratings[j]
                denom += abs(w)
                if best_source is None or w > best_source[0]:
                    best_source = (w, foods[j])
            if denom == 0:
                continue
            cf_score = num / denom
            food = db.session.get(Food, candidate_id)
            # Goal constraint: blend CF affinity with goal fit.
            goal_fit = _cosine(_food_features(food), goal_target)
            score = round(0.7 * cf_score + 0.3 * goal_fit, 4)
            scored.append((food, score, cf_score, best_source))
        scored.sort(key=lambda t: t[1], reverse=True)
        return self._build_meal_results(scored, user, goal, limit, cf=True)

    def _build_meal_results(self, scored, user, goal, limit, cf=False):
        results = []
        for entry in scored[:limit]:
            if cf:
                food, score, cf_score, best_source = entry
                source_name = db.session.get(Food, best_source[1]).name if best_source else "your history"
                reason = (f"Similar to {source_name}, which you often log "
                          f"(CF score {cf_score:.2f})")
            else:
                food, score = entry
                reason = self._food_goal_reason(food, goal)
            results.append({
                "item_id": food.id, "name": food.name, "score": round(score, 4),
                "reason": reason, "category": food.category,
                "calories": food.calories, "protein": food.protein,
                "carbs": food.carbs, "fat": food.fat,
                "serving_size": food.serving_size,
            })
        return results

    def _food_goal_reason(self, food, goal):
        goal_type = goal.goal_type if goal else "maintain"
        goal_words = {"lose": "weight-loss", "gain": "muscle-gain", "maintain": "maintenance"}
        bits = [f"Fits your {goal_words[goal_type]} goal"]
        if food.protein >= 15:
            bits.append(f"high protein ({food.protein:.0f}g per serving)")
        if goal_type == "lose" and food.calories <= 300:
            bits.append("low-calorie option")
        if goal_type == "gain" and food.calories >= 300:
            bits.append("energy-dense for a calorie surplus")
        return f"{'; '.join(bits)}"

    # --------------------------------------------------------------- workouts

    def recommend_workouts(self, user, limit=5):
        goal = user.active_goal
        workout_count = user.workout_logs.count()
        if workout_count >= self.cf_min_workout_logs:
            strategy = "cf"
            results = self._cf_workouts(user, goal, limit)
        else:
            strategy = "cb"
            results = self._content_based_workouts(user, goal, limit)

        today = datetime.utcnow()
        for r in results:
            rec = Recommendation(
                user_id=user.id, rec_type="workout", item_id=r["item_id"],
                score=r["score"], reason=r["reason"], created_at=today,
            )
            db.session.add(rec)
        return results, strategy

    def _content_based_workouts(self, user, goal, limit):
        goal_type = goal.goal_type if goal else "maintain"
        target = _EXERCISE_GOAL_VECTORS[goal_type]
        exercises = Exercise.query.all()
        candidates = [
            e for e in exercises
            if not self._recommended_recently(user, e.id, "workout")
        ]
        if not candidates:
            candidates = exercises
        scored = self._rank_by_similarity(candidates, _exercise_features, target)
        return self._build_workout_results(scored, user, goal, limit)

    def _cf_workouts(self, user, goal, limit):
        goal_type = goal.goal_type if goal else "maintain"
        rows = db.session.query(WorkoutLog.user_id, WorkoutLog.exercise_id,
                                db.func.sum(WorkoutLog.duration_min)).group_by(
            WorkoutLog.user_id, WorkoutLog.exercise_id).all()
        users = sorted({r[0] for r in rows})
        exercises = sorted({r[1] for r in rows})
        if len(users) < 2 or len(exercises) < 2:
            return self._content_based_workouts(user, goal, limit)

        u_index = {u: i for i, u in enumerate(users)}
        e_index = {e: i for i, e in enumerate(exercises)}
        matrix = np.zeros((len(users), len(exercises)))
        for uid, eid, minutes in rows:
            matrix[u_index[uid], e_index[eid]] = math.log1p(minutes)

        sim = _cosine_similarity_matrix(matrix.T)
        my_ratings = np.zeros(len(exercises))
        for uid, eid, minutes in rows:
            if uid == user.id:
                my_ratings[e_index[eid]] = math.log1p(minutes)
        done_by_me = {e for e in exercises if my_ratings[e_index[e]] > 0}

        scored = []
        goal_target = _EXERCISE_GOAL_VECTORS[goal_type]
        for candidate_id in exercises:
            if candidate_id in done_by_me or self._recommended_recently(user, candidate_id, "workout"):
                continue
            ci = e_index[candidate_id]
            denom, num = 0.0, 0.0
            best_source = None
            for j in range(len(exercises)):
                w = sim[ci, j]
                if w <= 0 or my_ratings[j] <= 0:
                    continue
                num += w * my_ratings[j]
                denom += abs(w)
                if best_source is None or w > best_source[0]:
                    best_source = (w, exercises[j])
            if denom == 0:
                continue
            cf_score = num / denom
            exercise = db.session.get(Exercise, candidate_id)
            goal_fit = _cosine(_exercise_features(exercise), goal_target)
            score = round(0.7 * cf_score + 0.3 * goal_fit, 4)
            scored.append((exercise, score, cf_score, best_source))
        scored.sort(key=lambda t: t[1], reverse=True)
        return self._build_workout_results(scored, user, goal, limit, cf=True)

    def _build_workout_results(self, scored, user, goal, limit, cf=False):
        weight = user.weight if user.weight else 65.0
        results = []
        for entry in scored[:limit]:
            if cf:
                exercise, score, cf_score, best_source = entry
                source_name = db.session.get(Exercise, best_source[1]).name if best_source else "your history"
                reason = (f"Similar to {source_name}, which you do often "
                          f"(CF score {cf_score:.2f})")
            else:
                exercise, score = entry
                goal_type = goal.goal_type if goal else "maintain"
                burn = met_calories(exercise.met_value, weight, 30)
                goal_words = {"lose": "calorie-burning", "gain": "muscle-building",
                              "maintain": "all-round"}
                reason = (f"{goal_words[goal_type].capitalize()} {exercise.category}: "
                          f"burns ~{burn:.0f} kcal in 30 min at {weight:.0f} kg")
            results.append({
                "item_id": exercise.id, "name": exercise.name, "score": round(score, 4),
                "reason": reason, "category": exercise.category,
                "met_value": exercise.met_value,
            })
        return results

    # ---------------------------------------------------------------- helpers

    def _rank_by_similarity(self, items, feature_fn, target):
        """Cosine-rank `items` against `target`; return [(item, score)] sorted."""
        scored = [(item, round(float(_cosine(feature_fn(item), target)), 4)) for item in items]
        scored.sort(key=lambda t: t[1], reverse=True)
        return scored

    @staticmethod
    def _logged_today(user, food_id):
        return user.meal_logs.filter(
            MealLog.food_id == food_id, MealLog.log_date == date.today()).first() is not None

    @staticmethod
    def _recommended_recently(user, item_id, rec_type):
        since = datetime.utcnow() - timedelta(hours=24)
        return user.recommendations.filter(
            Recommendation.item_id == item_id,
            Recommendation.rec_type == rec_type,
            Recommendation.created_at >= since).first() is not None


def _cosine(a, b):
    """Cosine similarity between two numpy vectors."""
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))
