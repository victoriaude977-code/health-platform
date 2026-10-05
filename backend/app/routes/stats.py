"""Statistics API (Objective 4 - Data Visualization).

Feeds the frontend ECharts dashboards: daily summary, daily/weekly/monthly
trends, and macro-nutrient breakdown.
"""
from collections import defaultdict
from datetime import date, timedelta

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app import db
from app.models import Food, MealLog, WorkoutLog
from app.utils.auth import get_current_user

stats_bp = Blueprint("stats", __name__, url_prefix="/api/stats")


@stats_bp.get("/daily")
@jwt_required()
def daily_summary():
    """One day's totals: calories in/out/net vs goal target + macro breakdown."""
    user = get_current_user()
    raw_date = request.args.get("date")
    target_date = date.fromisoformat(raw_date) if raw_date else date.today()

    meals = db.session.query(
        db.func.sum(MealLog.quantity * Food.calories),
        db.func.sum(MealLog.quantity * Food.protein),
        db.func.sum(MealLog.quantity * Food.carbs),
        db.func.sum(MealLog.quantity * Food.fat),
    ).join(Food, MealLog.food_id == Food.id).filter(
        MealLog.user_id == user.id, MealLog.log_date == target_date).first()

    calories_out = db.session.query(
        db.func.sum(WorkoutLog.calories_burned),
    ).filter(
        WorkoutLog.user_id == user.id, WorkoutLog.log_date == target_date).scalar()

    calories_in = round(float(meals[0] or 0), 1)
    goal = user.active_goal
    target = goal.daily_calorie_target if goal else None
    return jsonify({
        "date": target_date.isoformat(),
        "calories_in": calories_in,
        "calories_out": round(float(calories_out or 0), 1),
        "net": round(calories_in - float(calories_out or 0), 1),
        "daily_target": target,
        "remaining": round(target - calories_in, 1) if target else None,
        "goal_type": goal.goal_type if goal else None,
        "macros": {
            "protein": round(float(meals[1] or 0), 1),
            "carbs": round(float(meals[2] or 0), 1),
            "fat": round(float(meals[3] or 0), 1),
        },
    })


@stats_bp.get("/trends")
@jwt_required()
def daily_trends():
    """Per-day series for the last N days (zero-filled) - ECharts line charts."""
    user = get_current_user()
    try:
        days = min(max(int(request.args.get("days", 30)), 1), 365)
    except ValueError:
        return jsonify(error="Invalid days parameter"), 400

    end = date.today()
    start = end - timedelta(days=days - 1)

    meal_rows = db.session.query(
        MealLog.log_date,
        db.func.sum(MealLog.quantity * Food.calories),
        db.func.sum(MealLog.quantity * Food.protein),
        db.func.sum(MealLog.quantity * Food.carbs),
        db.func.sum(MealLog.quantity * Food.fat),
    ).join(Food, MealLog.food_id == Food.id).filter(
        MealLog.user_id == user.id,
        MealLog.log_date >= start, MealLog.log_date <= end,
    ).group_by(MealLog.log_date).all()

    workout_rows = db.session.query(
        WorkoutLog.log_date, db.func.sum(WorkoutLog.calories_burned),
    ).filter(
        WorkoutLog.user_id == user.id,
        WorkoutLog.log_date >= start, WorkoutLog.log_date <= end,
    ).group_by(WorkoutLog.log_date).all()

    meals_by_day = {d: (ci, p, c, f) for d, ci, p, c, f in meal_rows}
    workouts_by_day = {d: co for d, co in workout_rows}

    series = []
    for offset in range(days):
        d = start + timedelta(days=offset)
        ci, p, c, f = meals_by_day.get(d, (0, 0, 0, 0))
        co = workouts_by_day.get(d, 0)
        series.append({
            "date": d.isoformat(),
            "calories_in": round(float(ci), 1),
            "calories_out": round(float(co), 1),
            "net": round(float(ci) - float(co), 1),
            "macros": {
                "protein": round(float(p), 1),
                "carbs": round(float(c), 1),
                "fat": round(float(f), 1),
            },
        })
    return jsonify(days=days, series=series)


@stats_bp.get("/monthly")
@jwt_required()
def monthly_trends():
    """Per-month aggregates for the last N months."""
    user = get_current_user()
    try:
        months = min(max(int(request.args.get("months", 6)), 1), 24)
    except ValueError:
        return jsonify(error="Invalid months parameter"), 400

    end = date.today()
    start = _add_months(end.replace(day=1), -(months - 1))

    # Group per day in SQL (required by MySQL's only_full_group_by; SQLite
    # silently accepted the un-grouped form and lumped everything into one
    # bucket). Months are then aggregated in Python.
    meal_rows = db.session.query(
        MealLog.log_date, db.func.sum(MealLog.quantity * Food.calories),
    ).join(Food, MealLog.food_id == Food.id).filter(
        MealLog.user_id == user.id, MealLog.log_date >= start,
    ).group_by(MealLog.log_date).all()
    workout_rows = db.session.query(
        WorkoutLog.log_date, db.func.sum(WorkoutLog.calories_burned),
    ).filter(
        WorkoutLog.user_id == user.id, WorkoutLog.log_date >= start,
    ).group_by(WorkoutLog.log_date).all()

    buckets = defaultdict(lambda: {"calories_in": 0.0, "calories_out": 0.0})
    for d, ci in meal_rows:
        buckets[f"{d.year}-{d.month:02d}"]["calories_in"] += float(ci)
    for d, co in workout_rows:
        buckets[f"{d.year}-{d.month:02d}"]["calories_out"] += float(co)

    series = []
    for offset in range(months):
        d = _add_months(start, offset)
        key = f"{d.year}-{d.month:02d}"
        bucket = buckets.get(key, {"calories_in": 0.0, "calories_out": 0.0})
        series.append({
            "month": key,
            "calories_in": round(bucket["calories_in"], 1),
            "calories_out": round(bucket["calories_out"], 1),
        })
    return jsonify(months=months, series=series)


def _add_months(d, n):
    """Return the first day of the month `n` months away from date `d`."""
    month_index = d.year * 12 + (d.month - 1) + n
    return date(month_index // 12, month_index % 12 + 1, 1)
