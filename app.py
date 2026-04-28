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
    make_response,
)

from config import config
from extensions import db, migrate, login_manager, csrf
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
        if "theme" in request.cookies:
            session["theme"] = request.cookies.get("theme")

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
        if "set_lang" in request.args:
            lang = request.args["set_lang"]
            response = make_response(redirect(url_for("index")))
            if lang == "pl":
                response.set_cookie("googtrans", "/en/pl", max_age=30 * 24 * 60 * 60)
            elif lang == "en":
                response.set_cookie("googtrans", "/en/en", max_age=30 * 24 * 60 * 60)
            return response
        return render_template("index.html")

    @app.route("/health")
    def health():
        return jsonify(status="ok"), 200

    @app.context_processor
    def inject_theme():
        theme_setting = session.get("theme", "light")
        return dict(current_theme_class=f"{theme_setting}-mode")

    return app


# WSGI / Flask CLI entrypoint
app = create_app()


if __name__ == "__main__":
    app.run(debug=app.config.get("DEBUG", False))
