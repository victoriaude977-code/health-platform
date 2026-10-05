"""Route package: collects every API blueprint."""
from app.routes.auth import auth_bp
from app.routes.profile import profile_bp
from app.routes.foods import foods_bp
from app.routes.exercises import exercises_bp
from app.routes.meals import meals_bp
from app.routes.workouts import workouts_bp
from app.routes.goals import goals_bp
from app.routes.stats import stats_bp
from app.routes.recommendations import recommendations_bp
from app.routes.recognition import recognition_bp

__all__ = [
    "auth_bp", "profile_bp", "foods_bp", "exercises_bp", "meals_bp",
    "workouts_bp", "goals_bp", "stats_bp", "recommendations_bp", "recognition_bp",
]
