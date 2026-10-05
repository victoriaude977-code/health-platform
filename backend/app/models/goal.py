"""Goal model: one fitness goal per time range, governing diet + workouts."""
from app import db


class Goal(db.Model):
    __tablename__ = "goals"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    goal_type = db.Column(db.String(20), nullable=False)      # lose / gain / maintain
    target_weight = db.Column(db.Float, nullable=True)        # kg, for lose/gain goals
    daily_calorie_target = db.Column(db.Integer, nullable=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "goal_type": self.goal_type,
            "target_weight": self.target_weight,
            "daily_calorie_target": self.daily_calorie_target,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
        }
