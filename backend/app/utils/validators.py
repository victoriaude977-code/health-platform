"""
Request validation helpers.

Per the project's risk register ("inconsistent user logging"), input is
validated on the backend (and again on the frontend) before touching the DB.
"""
from datetime import date, datetime

VALID_MEAL_TYPES = {"breakfast", "lunch", "dinner", "snack"}
VALID_INTENSITIES = {"light", "moderate", "vigorous"}
VALID_GOAL_TYPES = {"lose", "gain", "maintain"}


class ValidationError(ValueError):
    """Raised by validators; caught by routes and returned as a 400."""


def require_fields(data, *fields):
    """Every named field must be present and non-empty."""
    for field in fields:
        if data.get(field) in (None, ""):
            raise ValidationError(f"Missing required field: {field}")


def require_choice(value, choices, field):
    """Value must be one of the allowed choices."""
    if value not in choices:
        raise ValidationError(f"Invalid {field}: must be one of {sorted(choices)}")


def parse_positive_float(data, field, maximum=None):
    """Return data[field] as a float > 0, or raise ValidationError."""
    try:
        value = float(data.get(field))
    except (TypeError, ValueError):
        raise ValidationError(f"Invalid {field}: must be a number")
    if value <= 0:
        raise ValidationError(f"Invalid {field}: must be greater than 0")
    if maximum is not None and value > maximum:
        raise ValidationError(f"Invalid {field}: must be at most {maximum}")
    return value


def parse_optional_float(data, field, minimum=None, maximum=None):
    """Return data[field] as a float or None; validates range when present."""
    if data.get(field) in (None, ""):
        return None
    try:
        value = float(data.get(field))
    except (TypeError, ValueError):
        raise ValidationError(f"Invalid {field}: must be a number")
    if minimum is not None and value < minimum:
        raise ValidationError(f"Invalid {field}: must be at least {minimum}")
    if maximum is not None and value > maximum:
        raise ValidationError(f"Invalid {field}: must be at most {maximum}")
    return value


def parse_date(data, field="log_date", default=None):
    """Return data[field] as a date object; today when absent and no default."""
    raw = data.get(field)
    if raw in (None, ""):
        return default or date.today()
    try:
        return datetime.strptime(str(raw), "%Y-%m-%d").date()
    except ValueError:
        raise ValidationError(f"Invalid {field}: expected YYYY-MM-DD")
