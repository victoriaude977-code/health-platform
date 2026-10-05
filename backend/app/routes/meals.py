"""Meal Logs API (Objective 2 - Meal Logging)."""
from datetime import date

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app import db
from app.models import Food, MealLog
from app.utils.auth import get_current_user
from app.utils.validators import (
    ValidationError, VALID_MEAL_TYPES, parse_date, parse_positive_float, require_choice,
)

meals_bp = Blueprint("meals", __name__, url_prefix="/api/meals")


@meals_bp.post("")
@jwt_required()
def log_meal():
    """Log a meal: food + number of servings + mealtime. Nutrition is computed
    from the food reference table (single source of truth)."""
    user = get_current_user()
    data = request.get_json(silent=True) or {}
    try:
        food_id = int(data.get("food_id") or 0)
        meal_type = str(data.get("meal_type") or "")
        require_choice(meal_type, VALID_MEAL_TYPES, "meal_type")
        quantity = parse_positive_float(data, "quantity", maximum=50)
    except (ValidationError, ValueError) as e:
        return jsonify(error=str(e)), 400
    food = db.session.get(Food, food_id)
    if food is None:
        return jsonify(error="Food not found"), 404

    log = MealLog(
        user_id=user.id, food_id=food_id, meal_type=meal_type,
        quantity=quantity, log_date=parse_date(data),
    )
    db.session.add(log)
    db.session.commit()
    return jsonify(log=log.to_dict()), 201


@meals_bp.get("")
@jwt_required()
def list_meals():
    user = get_current_user()
    raw_date = request.args.get("date")
    target_date = date.fromisoformat(raw_date) if raw_date else date.today()
    logs = (user.meal_logs.filter(MealLog.log_date == target_date)
            .order_by(MealLog.id.desc()).all())
    return jsonify(items=[m.to_dict() for m in logs], date=target_date.isoformat())


@meals_bp.put("/<int:log_id>")
@jwt_required()
def update_meal(log_id):
    user = get_current_user()
    log = user.meal_logs.filter_by(id=log_id).first()
    if log is None:
        return jsonify(error="Meal log not found"), 404
    data = request.get_json(silent=True) or {}
    try:
        if "meal_type" in data:
            require_choice(str(data.get("meal_type")), VALID_MEAL_TYPES, "meal_type")
            log.meal_type = data["meal_type"]
        if "quantity" in data:
            log.quantity = parse_positive_float(data, "quantity", maximum=50)
    except ValidationError as e:
        return jsonify(error=str(e)), 400
    db.session.commit()
    return jsonify(log=log.to_dict())


@meals_bp.delete("/<int:log_id>")
@jwt_required()
def delete_meal(log_id):
    user = get_current_user()
    log = user.meal_logs.filter_by(id=log_id).first()
    if log is None:
        return jsonify(error="Meal log not found"), 404
    db.session.delete(log)
    db.session.commit()
    return jsonify(message="Meal log deleted")
