import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration loaded from environment variables."""

    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")

    # ---- Database (Aiven PostgreSQL) ---- #
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME')}"
    )

    # SSL connection args for Aiven (requires ca.pem)
    _ssl_root_cert = os.getenv("DB_SSLROOTCERT", "")
    SQLALCHEMY_ENGINE_OPTIONS = (
        {
            "connect_args": {
                "sslmode": "require",
                "sslrootcert": _ssl_root_cert,
            }
        }
        if _ssl_root_cert
        else {}
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ---- MTN MoMo ---- #
    MOMO_API_KEY = os.getenv("MOMO_API_KEY", "")
    MOMO_USER_ID = os.getenv("MOMO_USER_ID", "")
    MOMO_BASE_URL = os.getenv("MOMO_BASE_URL", "https://sandbox.momodeveloper.mtn.com")
    MOMO_SUBSCRIPTION_KEY = os.getenv("MOMO_SUBSCRIPTION_KEY", "")

    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = os.getenv("FLASK_DEBUG", "1") == "1"
