"""Goals API (Objective 5 - personalized, goal-driven recommendations)."""
from datetime import date, timedelta

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app import db
from app.models import Goal
from app.utils.auth import get_current_user
from app.utils.calories import daily_calorie_target
from app.utils.validators import (
    ValidationError, VALID_GOAL_TYPES, parse_date, require_choice, require_fields,
)

goals_bp = Blueprint("goals", __name__, url_prefix="/api/goals")


@goals_bp.get("")
@jwt_required()
def list_goals():
    user = get_current_user()
    goals = user.goals.order_by(Goal.id.desc()).limit(10).all()
    return jsonify(items=[g.to_dict() for g in goals],
                   active_goal=user.active_goal.to_dict() if user.active_goal else None)


@goals_bp.post("")
@jwt_required()
def create_goal():
    """Create a goal. The daily calorie target is computed from the user's
    body profile (Mifflin-St Jeor) unless explicitly provided."""
    user = get_current_user()
    data = request.get_json(silent=True) or {}
    try:
        require_fields(data, "goal_type")
        goal_type = str(data["goal_type"])
        require_choice(goal_type, VALID_GOAL_TYPES, "goal_type")
    except ValidationError as e:
        return jsonify(error=str(e)), 400

    start_date = parse_date(data, "start_date", default=date.today())
    # Default end: 12 weeks from the start date.
    end_date = parse_date(data, "end_date", default=start_date + timedelta(weeks=12))
    if end_date < start_date:
        return jsonify(error="end_date must be on or after start_date"), 400

    if "daily_calorie_target" in data and data["daily_calorie_target"] not in (None, ""):
        target = int(data["daily_calorie_target"])
    else:
        if None in (user.height, user.weight, user.age, user.gender):
            return jsonify(
                error="Complete your profile (height, weight, age, gender) first, "
                      "or provide daily_calorie_target manually"), 400
        target = daily_calorie_target(user.weight, user.height, user.age, user.gender, goal_type)

    goal = Goal(
        user_id=user.id, goal_type=goal_type,
        target_weight=float(data["target_weight"]) if data.get("target_weight") else None,
        daily_calorie_target=target, start_date=start_date, end_date=end_date,
    )
    db.session.add(goal)
    db.session.commit()
    return jsonify(goal=goal.to_dict()), 201


@goals_bp.put("/<int:goal_id>")
@jwt_required()
def update_goal(goal_id):
    user = get_current_user()
    goal = user.goals.filter_by(id=goal_id).first()
    if goal is None:
        return jsonify(error="Goal not found"), 404
    data = request.get_json(silent=True) or {}
    if "goal_type" in data:
        if data["goal_type"] not in VALID_GOAL_TYPES:
            return jsonify(error="Invalid goal_type"), 400
        goal.goal_type = data["goal_type"]
    if "target_weight" in data:
        goal.target_weight = float(data["target_weight"]) if data["target_weight"] else None
    if "daily_calorie_target" in data and data["daily_calorie_target"] not in (None, ""):
        goal.daily_calorie_target = int(data["daily_calorie_target"])
    if "end_date" in data:
        goal.end_date = parse_date(data, "end_date")
    db.session.commit()
    return jsonify(goal=goal.to_dict())


@goals_bp.delete("/<int:goal_id>")
@jwt_required()
def delete_goal(goal_id):
    user = get_current_user()
    goal = user.goals.filter_by(id=goal_id).first()
    if goal is None:
        return jsonify(error="Goal not found"), 404
    db.session.delete(goal)
    db.session.commit()
    return jsonify(message="Goal deleted")
