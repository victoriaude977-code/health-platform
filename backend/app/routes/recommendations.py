"""Recommendations API (Objective 5 - Personalized Recommendations).

GET /api/recommendations        generates fresh recommendations (stored with a
                                `reason` for explainability) and returns them.
GET /api/recommendations/history  returns previously generated recommendations.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app import db
from app.models import Exercise, Food, Recommendation
from app.services.recommender import RecommendationEngine
from app.utils.auth import get_current_user

recommendations_bp = Blueprint("recommendations", __name__, url_prefix="/api/recommendations")

engine = RecommendationEngine()


@recommendations_bp.get("")
@jwt_required()
def get_recommendations():
    user = get_current_user()
    rec_type = request.args.get("type", "meal")
    if rec_type not in ("meal", "workout"):
        return jsonify(error="type must be 'meal' or 'workout'"), 400
    try:
        limit = min(max(int(request.args.get("limit", 5)), 1), 20)
    except ValueError:
        return jsonify(error="Invalid limit"), 400

    if rec_type == "meal":
        items, strategy = engine.recommend_meals(user, limit)
    else:
        items, strategy = engine.recommend_workouts(user, limit)
    db.session.commit()
    return jsonify(items=items, strategy=strategy,
                   explanation=_STRATEGY_LABELS[strategy])


@recommendations_bp.get("/history")
@jwt_required()
def recommendation_history():
    user = get_current_user()
    rec_type = request.args.get("type")
    query = user.recommendations
    if rec_type in ("meal", "workout"):
        query = query.filter(Recommendation.rec_type == rec_type)
    recs = query.order_by(Recommendation.created_at.desc()).limit(50).all()

    items = []
    for rec in recs:
        model = Food if rec.rec_type == "meal" else Exercise
        item = db.session.get(model, rec.item_id)
        items.append({
            "id": rec.id,
            "rec_type": rec.rec_type,
            "item_id": rec.item_id,
            "item_name": item.name if item else "(removed)",
            "score": rec.score,
            "reason": rec.reason,
            "created_at": rec.created_at.isoformat() if rec.created_at else None,
        })
    return jsonify(items=items)


_STRATEGY_LABELS = {
    "cf": "Collaborative filtering (enough logging history)",
    "cb": "Content-based fallback (cold start: not enough history yet)",
}
