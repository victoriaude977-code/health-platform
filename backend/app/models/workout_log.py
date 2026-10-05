"""WorkoutLog model: one logged workout (exercise, duration, intensity)."""
from app import db


class WorkoutLog(db.Model):
    __tablename__ = "workout_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercises.id"), nullable=False)
    duration_min = db.Column(db.Integer, nullable=False)          # minutes
    intensity = db.Column(db.String(20), nullable=False, default="moderate")
    calories_burned = db.Column(db.Float, nullable=False)
    log_date = db.Column(db.Date, nullable=False, index=True)

    exercise = db.relationship("Exercise")

    def to_dict(self):
        return {
            "id": self.id,
            "exercise_id": self.exercise_id,
            "exercise_name": self.exercise.name,
            "category": self.exercise.category,
            "met_value": self.exercise.met_value,
            "duration_min": self.duration_min,
            "intensity": self.intensity,
            "calories_burned": self.calories_burned,
            "log_date": self.log_date.isoformat(),
        }
