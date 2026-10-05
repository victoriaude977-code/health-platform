"""
Calorie calculations.

* Workout calories use the MET formula from the design document:
      kcal = MET x body weight (kg) x duration (hours)
  with an intensity adjustment factor.
* Daily calorie targets use the Mifflin-St Jeor BMR equation, adjusted by
  an activity factor and the user's goal (lose / gain / maintain).
"""

# Intensity multipliers applied on top of an activity's MET value.
INTENSITY_FACTORS = {"light": 0.85, "moderate": 1.0, "vigorous": 1.2}

# Activity multipliers (TDEE = BMR x factor). Default: lightly active.
ACTIVITY_FACTORS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
}

# Goal adjustments applied to TDEE (kcal/day).
GOAL_ADJUSTMENTS = {"lose": -400, "gain": +300, "maintain": 0}

MIN_CALORIE_TARGET = 1200  # never recommend below this


def met_calories(met_value, weight_kg, duration_min, intensity="moderate"):
    """kcal = MET x weight (kg) x hours, scaled by the intensity factor."""
    factor = INTENSITY_FACTORS.get(intensity, 1.0)
    return round(met_value * weight_kg * (duration_min / 60.0) * factor, 1)


def bmr_mifflin_st_jeor(weight_kg, height_cm, age, gender):
    """Basal metabolic rate (kcal/day), Mifflin-St Jeor equation."""
    base = 10 * weight_kg + 6.25 * height_cm - 5 * age
    if gender == "male":
        return base + 5
    return base - 161  # female and other


def tdee(weight_kg, height_cm, age, gender, activity="light"):
    """Total daily energy expenditure (kcal/day)."""
    return bmr_mifflin_st_jeor(weight_kg, height_cm, age, gender) * ACTIVITY_FACTORS.get(activity, 1.375)


def daily_calorie_target(weight_kg, height_cm, age, gender, goal_type, activity="light"):
    """Daily calorie budget derived from TDEE and the fitness goal."""
    maintenance = tdee(weight_kg, height_cm, age, gender, activity)
    target = maintenance + GOAL_ADJUSTMENTS.get(goal_type, 0)
    return int(max(target, MIN_CALORIE_TARGET))
