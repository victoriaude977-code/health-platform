"""Recommendation model: stores generated meal/workout recommendations.

Each row carries a `reason` so every recommendation shown to the user is
explainable (a core design decision of this project).
"""
from datetime import datetime

from app import db


class Recommendation(db.Model):
    __tablename__ = "recommendations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    rec_type = db.Column(db.String(20), nullable=False)   # meal / workout
    item_id = db.Column(db.Integer, nullable=False)       # foods.id or exercises.id
    score = db.Column(db.Float, nullable=True)            # similarity / ranking score
    reason = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
