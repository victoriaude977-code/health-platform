"""MealLog model: one logged meal entry (a food, a quantity, a mealtime)."""
from datetime import datetime

from app import db


class MealLog(db.Model):
    __tablename__ = "meal_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    food_id = db.Column(db.Integer, db.ForeignKey("foods.id"), nullable=False)
    meal_type = db.Column(db.String(20), nullable=False)  # breakfast / lunch / dinner / snack
    quantity = db.Column(db.Float, nullable=False, default=1.0)  # number of servings
    log_date = db.Column(db.Date, nullable=False, index=True)

    food = db.relationship("Food")

    @property
    def calories(self):
        return round(self.food.calories * self.quantity, 1)

    @property
    def protein(self):
        return round(self.food.protein * self.quantity, 1)

    @property
    def carbs(self):
        return round(self.food.carbs * self.quantity, 1)

    @property
    def fat(self):
        return round(self.food.fat * self.quantity, 1)

    def to_dict(self):
        return {
            "id": self.id,
            "meal_type": self.meal_type,
            "quantity": self.quantity,
            "log_date": self.log_date.isoformat(),
            "food_id": self.food_id,
            "food_name": self.food.name,
            "serving_size": self.food.serving_size,
            "calories": self.calories,
            "protein": self.protein,
            "carbs": self.carbs,
            "fat": self.fat,
        }
