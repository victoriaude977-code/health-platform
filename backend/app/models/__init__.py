"""Model package: imports every table so `db.create_all()` sees all of them."""
from app.models.user import User
from app.models.goal import Goal
from app.models.food import Food
from app.models.exercise import Exercise
from app.models.meal_log import MealLog
from app.models.workout_log import WorkoutLog
from app.models.recommendation import Recommendation

__all__ = ["User", "Goal", "Food", "Exercise", "MealLog", "WorkoutLog", "Recommendation"]
