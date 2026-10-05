"""Workout Logs API (Objective 3 - Workout Logging).

Calories burned are computed by the backend with the MET formula:
    kcal = MET x body weight (kg) x hours  (x intensity factor)
"""
from datetime import date

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app import db
from app.models import Exercise, WorkoutLog
from app.utils.auth import get_current_user
from app.utils.calories import met_calories
from app.utils.validators import (
    ValidationError, VALID_INTENSITIES, parse_date, parse_positive_float, require_choice,
)

workouts_bp = Blueprint("workouts", __name__, url_prefix="/api/workouts")


@workouts_bp.post("")
@jwt_required()
def log_workout():
    user = get_current_user()
    data = request.get_json(silent=True) or {}
    try:
        exercise_id = int(data.get("exercise_id") or 0)
        intensity = str(data.get("intensity") or "moderate")
        require_choice(intensity, VALID_INTENSITIES, "intensity")
        duration_min = parse_positive_float(data, "duration_min", maximum=1440)
    except (ValidationError, ValueError) as e:
        return jsonify(error=str(e)), 400
    exercise = db.session.get(Exercise, exercise_id)
    if exercise is None:
        return jsonify(error="Exercise not found"), 404

    weight = user.weight if user.weight else 65.0  # default if profile incomplete
    calories = met_calories(exercise.met_value, weight, duration_min, intensity)
    log = WorkoutLog(
        user_id=user.id, exercise_id=exercise_id, duration_min=duration_min,
        intensity=intensity, calories_burned=calories, log_date=parse_date(data),
    )
    db.session.add(log)
    db.session.commit()
    return jsonify(log=log.to_dict()), 201


@workouts_bp.get("")
@jwt_required()
def list_workouts():
    user = get_current_user()
    raw_date = request.args.get("date")
    target_date = date.fromisoformat(raw_date) if raw_date else date.today()
    logs = (user.workout_logs.filter(WorkoutLog.log_date == target_date)
            .order_by(WorkoutLog.id.desc()).all())
    return jsonify(items=[w.to_dict() for w in logs], date=target_date.isoformat())


@workouts_bp.delete("/<int:log_id>")
@jwt_required()
def delete_workout(log_id):
    user = get_current_user()
    log = user.workout_logs.filter_by(id=log_id).first()
    if log is None:
        return jsonify(error="Workout log not found"), 404
    db.session.delete(log)
    db.session.commit()
    return jsonify(message="Workout log deleted")
