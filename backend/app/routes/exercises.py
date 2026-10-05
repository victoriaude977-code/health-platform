"""Exercises API: browse the exercise reference database."""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.models import Exercise

exercises_bp = Blueprint("exercises", __name__, url_prefix="/api/exercises")


@exercises_bp.get("")
@jwt_required()
def list_exercises():
    query = Exercise.query
    search = (request.args.get("search") or "").strip()
    if search:
        query = query.filter(Exercise.name.ilike(f"%{search}%"))
    category = request.args.get("category")
    if category:
        query = query.filter_by(category=category)
    exercises = query.order_by(Exercise.name).all()
    categories = [c[0] for c in
                  Exercise.query.with_entities(Exercise.category).distinct().order_by(Exercise.category)]
    return jsonify(items=[e.to_dict() for e in exercises], categories=categories)


@exercises_bp.get("/<int:exercise_id>")
@jwt_required()
def get_exercise(exercise_id):
    exercise = Exercise.query.get(exercise_id)
    if exercise is None:
        return jsonify(error="Exercise not found"), 404
    return jsonify(exercise=exercise.to_dict())
