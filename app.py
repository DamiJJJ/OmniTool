import os
import logging
from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request,
    session,
    jsonify,
)

from config import config
from extensions import db, migrate, login_manager, csrf, limiter
from utils import format_date


def create_app(config_name=None):
    """Application factory."""
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)
    config_class = config.get(config_name, config["default"])
    app.config.from_object(config_class)
    config_class.init_app(app)

    logging.basicConfig(
        level=logging.DEBUG if app.config.get("DEBUG") else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    app.jinja_env.filters["date"] = format_date

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"
    csrf.init_app(app)
    limiter.init_app(app)

    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Blueprints
    from modules.auth import auth_bp
    from modules.weather import weather_bp
    from modules.currency import currency_bp
    from modules.todo import todo_bp
    from modules.conversion import conversion_bp
    from modules.youtube import youtube_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(weather_bp)
    app.register_blueprint(currency_bp)
    app.register_blueprint(todo_bp)
    app.register_blueprint(conversion_bp)
    app.register_blueprint(youtube_bp)

    @app.before_request
    def before_request():
        theme = request.cookies.get("theme")
        if theme in ("dark", "light"):
            session["theme"] = theme

    @app.after_request
    def set_security_headers(response):
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdn.tailwindcss.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
            "font-src 'self' https://cdnjs.cloudflare.com https://fonts.gstatic.com; "
            "img-src 'self' data: https: blob:; "
            "frame-src https://www.youtube.com; "
            "connect-src 'self';"
        )
        return response

    @app.route("/set-theme", methods=["POST"])
    def set_theme():
        data = request.get_json(silent=True) or {}
        theme = data.get("theme")
        if theme in ["dark", "light"]:
            response = jsonify(success=True)
            response.set_cookie(
                "theme",
                theme,
                max_age=30 * 24 * 60 * 60,
                httponly=True,
                samesite="Lax",
            )
            return response
        return jsonify(success=False), 400

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/health")
    def health():
        return jsonify(status="ok"), 200

    @app.context_processor
    def inject_theme():
        theme_setting = session.get("theme", "light")
        return dict(
            current_theme_class=f"{theme_setting}-mode",
            current_theme=theme_setting,
        )

    return app


# WSGI / Flask CLI entrypoint
app = create_app()


if __name__ == "__main__":
    app.run(debug=app.config.get("DEBUG", False))
