"""Auth API: register, login, current user (Objective 1 - User Authentication)."""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required

from app import db
from app.models import User
from app.utils.auth import get_current_user
from app.utils.validators import ValidationError, parse_optional_float, require_fields

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    try:
        require_fields(data, "username", "email", "password")
    except ValidationError as e:
        return jsonify(error=str(e)), 400
    username = data["username"].strip()
    email = data["email"].strip().lower()
    password = data["password"]
    if len(password) < 6:
        return jsonify(error="Password must be at least 6 characters"), 400
    if User.query.filter_by(username=username).first():
        return jsonify(error="Username already taken"), 409
    if User.query.filter_by(email=email).first():
        return jsonify(error="Email already registered"), 409

    user = User(username=username, email=email)
    user.set_password(password)
    # Optional body profile at sign-up time.
    user.height = parse_optional_float(data, "height", 50, 250)
    user.weight = parse_optional_float(data, "weight", 20, 400)
    user.age = int(data["age"]) if str(data.get("age") or "").isdigit() else None
    if data.get("gender") in ("male", "female", "other"):
        user.gender = data["gender"]
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify(access_token=token, user=user.to_dict(include_goal=True)), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    identifier = (data.get("username") or data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    user = User.query.filter(
        (User.username == identifier) | (User.email == identifier)).first()
    if user is None or not user.check_password(password):
        return jsonify(error="Invalid username/email or password"), 401
    token = create_access_token(identity=str(user.id))
    return jsonify(access_token=token, user=user.to_dict(include_goal=True))


@auth_bp.get("/me")
@jwt_required()
def me():
    user = get_current_user()
    if user is None:
        return jsonify(error="User not found"), 404
    return jsonify(user=user.to_dict(include_goal=True))
