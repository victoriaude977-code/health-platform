"""JWT helpers."""
from flask_jwt_extended import get_jwt_identity

from app import db
from app.models import User


def get_current_user():
    """Load the User identified by the JWT in the current request (or None)."""
    identity = get_jwt_identity()
    if identity is None:
        return None
    return db.session.get(User, int(identity))
