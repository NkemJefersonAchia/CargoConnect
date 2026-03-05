import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration loaded from environment variables."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "postgresql://postgres:password@localhost:5432/cargoconnect"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MOMO_API_KEY = os.getenv("MOMO_API_KEY", "")
    MOMO_USER_ID = os.getenv("MOMO_USER_ID", "")
    MOMO_BASE_URL = os.getenv("MOMO_BASE_URL", "https://sandbox.momodeveloper.mtn.com")
    MOMO_SUBSCRIPTION_KEY = os.getenv("MOMO_SUBSCRIPTION_KEY", "")

    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = os.getenv("FLASK_DEBUG", "1") == "1"
