"""Foods API: browse/search the food reference database."""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.models import Food

foods_bp = Blueprint("foods", __name__, url_prefix="/api/foods")


@foods_bp.get("")
@jwt_required()
def list_foods():
    query = Food.query
    search = (request.args.get("search") or "").strip()
    if search:
        query = query.filter(Food.name.ilike(f"%{search}%"))
    category = request.args.get("category")
    if category:
        query = query.filter_by(category=category)
    total = query.count()
    try:
        page = max(int(request.args.get("page", 1)), 1)
        per_page = min(max(int(request.args.get("per_page", 50)), 1), 200)
    except ValueError:
        return jsonify(error="Invalid pagination"), 400
    foods = query.order_by(Food.name).offset((page - 1) * per_page).limit(per_page).all()
    categories = [c[0] for c in
                  Food.query.with_entities(Food.category).distinct().order_by(Food.category)]
    return jsonify(items=[f.to_dict() for f in foods], total=total, categories=categories)


@foods_bp.get("/<int:food_id>")
@jwt_required()
def get_food(food_id):
    food = Food.query.get(food_id)
    if food is None:
        return jsonify(error="Food not found"), 404
    return jsonify(food=food.to_dict())
