"""Food model: the reference database of foods with nutrition facts."""
from app import db


class Food(db.Model):
    __tablename__ = "foods"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    category = db.Column(db.String(30), nullable=False, index=True)
    # Nutrition values are PER SERVING (see serving_size).
    calories = db.Column(db.Float, nullable=False)   # kcal
    protein = db.Column(db.Float, nullable=False)    # g
    carbs = db.Column(db.Float, nullable=False)      # g
    fat = db.Column(db.Float, nullable=False)        # g
    serving_size = db.Column(db.String(50), nullable=True)  # e.g. "1 bowl (200g)"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "calories": self.calories,
            "protein": self.protein,
            "carbs": self.carbs,
            "fat": self.fat,
            "serving_size": self.serving_size,
        }
