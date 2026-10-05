"""Profile API: read/update the user's body profile and avatar.

Avatar can be a preset icon ("preset:<key>", rendered by the frontend) or an
uploaded picture (POST /api/profile/avatar, stored under uploads/avatars/ and
served at /uploads/avatars/<file>).
"""
import os
import uuid

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import jwt_required

from app import db
from app.utils.auth import get_current_user
from app.utils.validators import parse_optional_float

profile_bp = Blueprint("profile", __name__, url_prefix="/api/profile")

ALLOWED_IMAGE_EXTS = {"png", "jpg", "jpeg", "webp", "gif"}


@profile_bp.get("")
@jwt_required()
def get_profile():
    return jsonify(user=get_current_user().to_dict(include_goal=True))


@profile_bp.put("")
@jwt_required()
def update_profile():
    user = get_current_user()
    data = request.get_json(silent=True) or {}
    if "height" in data:
        user.height = parse_optional_float(data, "height", 50, 250)
    if "weight" in data:
        user.weight = parse_optional_float(data, "weight", 20, 400)
    if "age" in data:
        if not str(data.get("age") or "").isdigit():
            return jsonify(error="Invalid age: must be an integer"), 400
        user.age = int(data["age"])
    if "gender" in data and data["gender"] in ("male", "female", "other"):
        user.gender = data["gender"]
    # Avatar: accept a preset key or remove the avatar entirely (empty string).
    if "avatar" in data:
        avatar = str(data.get("avatar") or "")
        if avatar == "":
            user.avatar = None
        elif avatar.startswith("preset:") and len(avatar) <= 60:
            user.avatar = avatar
        else:
            return jsonify(error="Invalid avatar value"), 400
    db.session.commit()
    return jsonify(user=user.to_dict(include_goal=True))


@profile_bp.post("/avatar")
@jwt_required()
def upload_avatar():
    """Upload a profile picture (multipart form field `file`)."""
    user = get_current_user()
    file = request.files.get("file")
    if file is None or not file.filename:
        return jsonify(error="No file uploaded (send multipart field 'file')"), 400
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_IMAGE_EXTS:
        return jsonify(error=f"Unsupported file type: .{ext}. Allowed: {sorted(ALLOWED_IMAGE_EXTS)}"), 400

    data = file.read()
    if len(data) > current_app.config["MAX_CONTENT_LENGTH"]:
        return jsonify(error="File too large (max 2 MB)"), 400

    folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(folder, exist_ok=True)
    filename = f"{user.id}_{uuid.uuid4().hex}.{ext}"
    with open(os.path.join(folder, filename), "wb") as fh:
        fh.write(data)

    user.avatar = f"/uploads/avatars/{filename}"
    db.session.commit()
    return jsonify(user=user.to_dict(include_goal=True))
