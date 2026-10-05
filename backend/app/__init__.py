"""Flask application factory for the Intelligent Health Management Platform."""
import os

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

from config import Config

db = SQLAlchemy()
jwt = JWTManager()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    jwt.init_app(app)
    CORS(app, origins=[o.strip() for o in app.config["CORS_ORIGINS"].split(",") if o.strip()])

    # Import models so SQLAlchemy knows every table before create_all().
    from app import models  # noqa: F401

    # Register API blueprints under /api.
    from app.routes import (
        auth_bp, profile_bp, foods_bp, exercises_bp, meals_bp,
        workouts_bp, goals_bp, stats_bp, recommendations_bp, recognition_bp,
    )
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(foods_bp)
    app.register_blueprint(exercises_bp)
    app.register_blueprint(meals_bp)
    app.register_blueprint(workouts_bp)
    app.register_blueprint(goals_bp)
    app.register_blueprint(stats_bp)
    app.register_blueprint(recommendations_bp)
    app.register_blueprint(recognition_bp)

    # JSON error handlers: always answer with JSON, never an HTML error page.
    @app.errorhandler(404)
    def not_found(e):
        return jsonify(error="Not found"), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify(error="Method not allowed"), 405

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        return jsonify(error="Internal server error"), 500

    @app.errorhandler(413)
    def too_large(e):
        return jsonify(error="File too large (max 2 MB)"), 413

    # Serve uploaded avatars. send_from_directory prevents path traversal.
    @app.get("/uploads/avatars/<path:filename>")
    def uploaded_avatar(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    @app.get("/api/health")
    def health():
        """Liveness probe used by the frontend and by the cloud deployment."""
        return jsonify(status="ok", service="health-platform-api")

    return app
