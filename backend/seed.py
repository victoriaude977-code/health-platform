"""
Seed script: populates the reference databases (foods, exercises) and a few
demo users with logging history.

The demo users give the collaborative-filtering matrix real data, so the
recommendation engine can be demonstrated end-to-end:
  * a brand-new user has no logs  -> content-based fallback (cold start)
  * after 5 meal logs              -> switches to collaborative filtering

Idempotent: safe to run repeatedly (existing rows are kept).

    python seed.py
"""
import random
from datetime import date, timedelta

from app import create_app, db
from app.models import Exercise, Food, MealLog, User, WorkoutLog

# ---------------------------------------------------------------------------
# Foods: nutrition per serving. kcal / protein g / carbs g / fat g.
# (name, category, calories, protein, carbs, fat, serving_size)
# ---------------------------------------------------------------------------
FOODS = [
    # ---- staples ----
    ("White rice (cooked)", "staple", 260, 4.4, 57, 0.4, "1 bowl (200g)"),
    ("Brown rice (cooked)", "staple", 220, 4.6, 45, 1.8, "1 bowl (200g)"),
    ("Noodles (cooked)", "staple", 276, 9.0, 55, 1.4, "1 bowl (200g)"),
    ("Steamed bun (mantou)", "staple", 223, 7.0, 47, 1.1, "1 piece (100g)"),
    ("Pork dumplings", "staple", 460, 16, 50, 20, "8 pieces (200g)"),
    ("Whole-wheat bread", "staple", 148, 6.4, 27, 2.0, "2 slices (60g)"),
    ("Oatmeal", "staple", 150, 5.0, 27, 2.6, "1 bowl (40g dry)"),
    ("Corn on the cob", "staple", 129, 4.8, 29, 2.0, "1 ear (150g)"),
    ("Sweet potato", "staple", 129, 2.4, 30, 0.2, "1 medium (150g)"),
    ("Pasta (cooked)", "staple", 262, 9.2, 49, 2.0, "1 plate (200g)"),
    # ---- protein ----
    ("Grilled chicken breast", "protein", 165, 31, 0, 3.6, "1 piece (100g)"),
    ("Boiled eggs", "protein", 155, 13, 1.1, 10.6, "2 eggs (100g)"),
    ("Salmon", "protein", 208, 20, 0, 13, "1 fillet (100g)"),
    ("Lean beef", "protein", 250, 26, 0, 15, "1 serving (100g)"),
    ("Stir-fried pork", "protein", 242, 27, 0, 14, "1 serving (100g)"),
    ("Tofu", "protein", 76, 8.0, 1.9, 4.8, "1 serving (100g)"),
    ("Shrimp", "protein", 99, 24, 0.2, 0.3, "1 serving (100g)"),
    ("Whole milk", "protein", 150, 8.0, 12, 8.0, "1 cup (250ml)"),
    ("Greek yogurt", "protein", 100, 17, 6.0, 0.7, "1 cup (170g)"),
    ("Canned tuna", "protein", 116, 26, 0, 0.8, "1 can (100g)"),
    ("Lentils (cooked)", "protein", 230, 18, 40, 0.8, "1 bowl (200g)"),
    # ---- vegetables ----
    ("Broccoli (steamed)", "vegetable", 53, 4.3, 10, 0.9, "1 bowl (150g)"),
    ("Spinach", "vegetable", 23, 2.9, 3.6, 0.4, "1 bowl (100g)"),
    ("Carrots", "vegetable", 41, 0.9, 10, 0.2, "1 serving (100g)"),
    ("Tomato", "vegetable", 22, 1.1, 4.8, 0.2, "1 medium (120g)"),
    ("Cucumber", "vegetable", 23, 1.0, 5.4, 0.2, "1 medium (150g)"),
    ("Bok choy", "vegetable", 20, 2.2, 3.3, 0.3, "1 bowl (150g)"),
    ("Mixed salad", "vegetable", 33, 1.5, 6.7, 0.4, "1 bowl (100g)"),
    # ---- fruits ----
    ("Apple", "fruit", 95, 0.5, 25, 0.3, "1 medium (180g)"),
    ("Banana", "fruit", 105, 1.3, 27, 0.4, "1 medium (118g)"),
    ("Orange", "fruit", 62, 1.2, 15, 0.2, "1 medium (130g)"),
    ("Grapes", "fruit", 104, 1.1, 27, 0.2, "1 cup (150g)"),
    ("Watermelon", "fruit", 84, 1.7, 21, 0.4, "1 slice (280g)"),
    ("Strawberries", "fruit", 49, 1.0, 12, 0.5, "1 cup (150g)"),
    # ---- dairy ----
    ("Cheddar cheese", "dairy", 120, 7.5, 0.4, 10, "1 slice (30g)"),
    # ---- snacks ----
    ("Chocolate bar", "snack", 270, 4.0, 28, 16, "1 bar (50g)"),
    ("Potato chips", "snack", 320, 4.0, 32, 20, "1 bag (60g)"),
    ("Mixed nuts", "snack", 180, 5.0, 6.0, 16, "1 handful (30g)"),
    ("Protein bar", "snack", 220, 20, 25, 7.0, "1 bar (60g)"),
    ("Cookies", "snack", 145, 2.0, 21, 6.0, "3 pieces (30g)"),
    ("Ice cream", "snack", 145, 2.5, 17, 7.9, "1 scoop (70g)"),
    # ---- drinks ----
    ("Cola", "drink", 139, 0, 35, 0, "1 can (330ml)"),
    ("Orange juice", "drink", 112, 1.7, 26, 0.5, "1 cup (250ml)"),
    ("Bubble milk tea", "drink", 350, 5.0, 55, 12, "1 cup (500ml)"),
    ("Green tea", "drink", 2, 0, 0.5, 0, "1 cup (250ml)"),
    ("Sports drink", "drink", 130, 0, 33, 0, "1 bottle (500ml)"),
    # ---- fast food ----
    ("Hamburger", "fast_food", 500, 25, 46, 25, "1 burger (250g)"),
    ("French fries", "fast_food", 365, 4.0, 48, 17, "1 medium (117g)"),
    ("Pizza slice", "fast_food", 285, 12, 36, 10, "1 slice (107g)"),
    ("Fried chicken", "fast_food", 420, 30, 18, 26, "1 piece (150g)"),
    ("Instant noodles", "fast_food", 380, 8.0, 54, 14, "1 pack (85g)"),
]

# Exercises: MET values from the Compendium of Physical Activities.
# (name, category, met_value)
EXERCISES = [
    ("Running (8 km/h)", "cardio", 8.3),
    ("Jogging", "cardio", 7.0),
    ("Brisk walking", "cardio", 4.3),
    ("Cycling (moderate)", "cardio", 6.8),
    ("Jump rope", "cardio", 11.0),
    ("Swimming (freestyle)", "cardio", 8.3),
    ("HIIT workout", "cardio", 8.5),
    ("Aerobic dance", "cardio", 7.3),
    ("Hiking", "cardio", 6.0),
    ("Weight lifting", "strength", 3.5),
    ("Bodyweight training", "strength", 3.8),
    ("Yoga", "flexibility", 2.5),
    ("Stretching", "flexibility", 2.3),
    ("Pilates", "flexibility", 3.0),
    ("Basketball", "sports", 6.5),
    ("Football (soccer)", "sports", 7.0),
    ("Badminton", "sports", 5.5),
    ("Table tennis", "sports", 4.0),
]

# Demo users: (username, password, height, weight, age, gender, goal_type)
DEMO_USERS = [
    ("demo", "demo1234", 165, 55, 22, "female", "lose"),
    ("alice", "demo1234", 170, 62, 23, "female", "maintain"),
    ("bob", "demo1234", 180, 75, 24, "male", "gain"),
    ("carol", "demo1234", 158, 50, 21, "female", "maintain"),
    ("david", "demo1234", 175, 80, 25, "male", "lose"),
]

# Each demo user's typical foods (ids resolved by name) and workouts.
DEMO_DIETS = {
    "alice": ["Tofu", "Mixed salad", "Broccoli (steamed)", "Brown rice (cooked)", "Apple", "Greek yogurt"],
    "bob": ["Grilled chicken breast", "Boiled eggs", "Salmon", "Lean beef", "Oatmeal", "Protein bar", "Whole milk"],
    "carol": ["White rice (cooked)", "Noodles (cooked)", "Pork dumplings", "Bubble milk tea", "Banana", "Cookies"],
    "david": ["Hamburger", "French fries", "Pizza slice", "Fried chicken", "Cola", "Instant noodles"],
}
DEMO_WORKOUTS = {
    "alice": ["Yoga", "Brisk walking", "Pilates"],
    "bob": ["Weight lifting", "HIIT workout", "Bodyweight training"],
    "carol": ["Badminton", "Aerobic dance", "Table tennis"],
    "david": ["Basketball", "Running (8 km/h)", "Football (soccer)"],
}
MEAL_TYPES = ["breakfast", "lunch", "dinner", "snack"]


def seed_foods_and_exercises():
    if Food.query.count() == 0:
        for name, cat, kcal, p, c, f, size in FOODS:
            db.session.add(Food(name=name, category=cat, calories=kcal,
                                protein=p, carbs=c, fat=f, serving_size=size))
        print(f"Inserted {len(FOODS)} foods.")
    else:
        print(f"Foods table already populated ({Food.query.count()} rows).")

    if Exercise.query.count() == 0:
        for name, cat, met in EXERCISES:
            db.session.add(Exercise(name=name, category=cat, met_value=met))
        print(f"Inserted {len(EXERCISES)} exercises.")
    else:
        print(f"Exercises table already populated ({Exercise.query.count()} rows).")
    db.session.commit()


def seed_demo_users():
    foods = {f.name: f for f in Food.query.all()}
    exercises = {e.name: e for e in Exercise.query.all()}
    today = date.today()
    rng = random.Random(42)  # deterministic seed -> reproducible demo data

    for username, password, height, weight, age, gender, goal_type in DEMO_USERS:
        user = User.query.filter_by(username=username).first()
        if user is None:
            user = User(username=username, email=f"{username}@demo.local",
                        height=height, weight=weight, age=age, gender=gender)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            diet = DEMO_DIETS.get(username)
            if diet:
                # 14 days of meal history (2-3 meals/day from their diet).
                for offset in range(14, 0, -1):
                    day = today - timedelta(days=offset)
                    for _ in range(rng.randint(2, 3)):
                        name = rng.choice(diet)
                        db.session.add(MealLog(
                            user_id=user.id, food_id=foods[name].id,
                            meal_type=rng.choice(MEAL_TYPES),
                            quantity=round(rng.uniform(0.5, 2.0), 1), log_date=day))
                # 4 workouts in the last 14 days.
                for offset in rng.sample(range(1, 15), 4):
                    day = today - timedelta(days=offset)
                    name = rng.choice(DEMO_WORKOUTS[username])
                    ex = exercises[name]
                    db.session.add(WorkoutLog(
                        user_id=user.id, exercise_id=ex.id,
                        duration_min=rng.choice([20, 30, 45, 60]),
                        intensity=rng.choice(["light", "moderate", "moderate", "vigorous"]),
                        calories_burned=round(ex.met_value * weight * (rng.choice([30, 45]) / 60), 1),
                        log_date=day))
                db.session.commit()
                print(f"Created demo user '{username}' with 14 days of history.")
            else:
                # 'demo' stays log-free on purpose: it demonstrates the
                # cold-start path (content-based) before switching to CF.
                db.session.commit()
                print(f"Created demo user '{username}' (no history - cold-start demo).")
        else:
            print(f"Demo user '{username}' already exists.")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
        print("Tables ready.")
        seed_foods_and_exercises()
        seed_demo_users()
        print("Seeding complete. Demo login: demo / demo1234")
