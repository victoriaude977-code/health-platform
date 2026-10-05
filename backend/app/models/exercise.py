"""Exercise model: the reference database of exercises with MET values.

MET (Metabolic Equivalent of Task) values follow the Compendium of Physical
Activities. Calories burned = MET x body weight (kg) x duration (hours).
"""
from app import db


class Exercise(db.Model):
    __tablename__ = "exercises"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    category = db.Column(db.String(30), nullable=False, index=True)  # cardio / strength / flexibility / sports
    met_value = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "met_value": self.met_value,
        }
