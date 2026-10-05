"""
Application configuration.

Local development defaults are provided; every value can be overridden by
environment variables (or a backend/.env file), which is what the cloud
deployment will use:

    DATABASE_URL      full SQLAlchemy URL (mysql+pymysql://user:pass@host:3306/db)
    JWT_SECRET_KEY    secret used to sign JWT tokens (must change in production!)
    CORS_ORIGINS      comma-separated list of allowed frontend origins
"""
import os
from datetime import timedelta

from dotenv import load_dotenv

# Load backend/.env if present (does nothing if the file is missing).
load_dotenv()


class Config:
    # --- Security ---
    # NEVER ship the production deployment with this default secret.
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-secret-change-in-production")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)

    # --- Database ---
    # Local development: MySQL on the student machine (user created by setup).
    # Production: set DATABASE_URL in the environment, e.g.
    #   mysql+pymysql://tzc_app:STRONG_PASSWORD@db-host:3306/health_platform
    DATABASE_URL = os.environ.get(
        "DATABASE_URL",
        "mysql+pymysql://tzc_app:tzc_app_2026@127.0.0.1:3306/health_platform?charset=utf8mb4",
    )
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Recycle MySQL connections (the default MySQL wait_timeout is 8 h).
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_recycle": 28000, "pool_pre_ping": True}

    # --- CORS ---
    # Dev: the Vite server at localhost:5173. Production: set CORS_ORIGINS to
    # the deployed frontend URL, e.g. https://health.example.com
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")

    # --- Avatar uploads ---
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads", "avatars")
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2 MB per request

    # --- Recommendation engine ---
    # Minimum number of meal/workout logs before collaborative filtering is
    # trusted; below this we switch to the content-based fallback (cold start).
    CF_MIN_MEAL_LOGS = 5
    CF_MIN_WORKOUT_LOGS = 3
    REC_LIMIT = 5  # items returned per recommendation request
