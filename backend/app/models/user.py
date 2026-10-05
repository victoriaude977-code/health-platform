"""User model: registered accounts and their body profile."""
from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

from app import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    # Body profile used by calorie / recommendation calculations.
    height = db.Column(db.Float, nullable=True)          # cm
    weight = db.Column(db.Float, nullable=True)          # kg
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(10), nullable=True)     # male / female / other
    # Avatar: either "preset:<key>" (built-in icon chosen on the frontend) or
    # "/uploads/avatars/<file>" (user-uploaded picture).
    avatar = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships (1:N).
    goals = db.relationship("Goal", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    meal_logs = db.relationship("MealLog", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    workout_logs = db.relationship("WorkoutLog", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    recommendations = db.relationship("Recommendation", backref="user", lazy="dynamic", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def active_goal(self):
        """The goal whose date range covers today (None if no goal set)."""
        today = datetime.utcnow().date()
        return (
            self.goals.filter(Goal.start_date <= today, Goal.end_date >= today)
            .order_by(Goal.id.desc())
            .first()
        )

    def to_dict(self, include_goal=False):
        data = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "height": self.height,
            "weight": self.weight,
            "age": self.age,
            "gender": self.gender,
            "avatar": self.avatar,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_goal:
            goal = self.active_goal
            data["active_goal"] = goal.to_dict() if goal else None
        return data


# Imported at the bottom to avoid a circular import (User -> Goal backref).
from app.models.goal import Goal  # noqa: E402
