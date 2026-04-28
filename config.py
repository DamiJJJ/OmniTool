import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Bazowa konfiguracja aplikacji."""

    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB
    REQUESTS_TIMEOUT = (5, 10)

    OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")
    CURRENCY_API_KEY = os.environ.get("CURRENCY_API_KEY")
    YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
    YOUTUBE_CHANNEL_ID = os.environ.get(
        "YOUTUBE_CHANNEL_ID", "UC1uYJszfaKTzbbz7jMiXBFg"
    )

    @classmethod
    def init_app(cls, app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-secret-key-change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///site.db")


class ProductionConfig(Config):
    DEBUG = False

    @classmethod
    def init_app(cls, app):
        if not os.environ.get("SECRET_KEY"):
            raise RuntimeError(
                "SECRET_KEY musi być ustawiony w środowisku produkcyjnym!"
            )
        db_url = os.environ.get("DATABASE_URL")
        if not db_url:
            raise RuntimeError(
                "DATABASE_URL musi być ustawiony w środowisku produkcyjnym!"
            )
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql+psycopg://", 1)
        elif db_url.startswith("postgresql://"):
            db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)
        app.config["SQLALCHEMY_DATABASE_URI"] = db_url

        # Twardsze cookie w produkcji
        app.config.update(
            SESSION_COOKIE_SECURE=True,
            SESSION_COOKIE_HTTPONLY=True,
            SESSION_COOKIE_SAMESITE="Lax",
            REMEMBER_COOKIE_SECURE=True,
            REMEMBER_COOKIE_HTTPONLY=True,
        )


class TestingConfig(Config):
    TESTING = True
    SECRET_KEY = "test-secret-key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
