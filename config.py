import os
from dotenv import load_dotenv

load_dotenv()


def normalize_db_url(db_url):
    """Normalizuje URL bazy do sterownika obsługiwanego przez aplikację.

    - postgres://  / postgresql://  -> postgresql+psycopg://
    - mysql://     / mysql+mysqldb:// -> mysql+pymysql://  (sterownik PyMySQL, czysty Python)
    Dzięki temu w stacku Portainera można podać prosty `mysql://user:pass@mariadb:3306/baza`,
    a aplikacja i tak użyje PyMySQL.
    """
    if not db_url:
        return db_url
    if db_url.startswith("postgres://"):
        return db_url.replace("postgres://", "postgresql+psycopg://", 1)
    if db_url.startswith("postgresql://"):
        return db_url.replace("postgresql://", "postgresql+psycopg://", 1)
    if db_url.startswith("mysql://"):
        return db_url.replace("mysql://", "mysql+pymysql://", 1)
    if db_url.startswith("mysql+mysqldb://"):
        return db_url.replace("mysql+mysqldb://", "mysql+pymysql://", 1)
    return db_url


class Config:
    """Bazowa konfiguracja aplikacji."""

    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB
    REQUESTS_TIMEOUT = (5, 10)

    # Odporność połączeń z bazą (MySQL/MariaDB zrywa bezczynne sesje)
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }

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
    SQLALCHEMY_DATABASE_URI = normalize_db_url(
        os.environ.get("DATABASE_URL", "sqlite:///site.db")
    )


class ProductionConfig(Config):
    DEBUG = False

    USE_PROXY_FIX = True

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
        app.config["SQLALCHEMY_DATABASE_URI"] = normalize_db_url(db_url)

        secure_cookies = os.environ.get("SESSION_COOKIE_SECURE", "true").lower() in (
            "1",
            "true",
            "yes",
            "on",
        )
        app.config.update(
            SESSION_COOKIE_SECURE=secure_cookies,
            SESSION_COOKIE_HTTPONLY=True,
            SESSION_COOKIE_SAMESITE="Lax",
            REMEMBER_COOKIE_SECURE=secure_cookies,
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
