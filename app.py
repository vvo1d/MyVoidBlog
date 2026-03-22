"""Application factory."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

from config import Config
from models import User, db

load_dotenv()

csrf = CSRFProtect()
login_manager = LoginManager()
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per hour"])


@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    return db.session.get(User, int(user_id))


def create_app(config_class: type = Config) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure directories exist
    for d in ("UPLOAD_DIR", "STATIC_UPLOAD_DIR"):
        Path(app.config[d]).mkdir(parents=True, exist_ok=True)

    # Init extensions
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "admin.login"
    limiter.init_app(app)

    # Rate limit login endpoint
    from views.admin import admin as admin_bp
    from views.public import public as public_bp

    limiter.limit("10 per minute")(admin_bp)

    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)

    # Exempt upload endpoint from CSRF for AJAX
    csrf.exempt(admin_bp)
    # Re-enable CSRF for non-upload routes handled by forms with tokens

    # Russian date filter
    MONTHS_FULL = [
        "", "января", "февраля", "марта", "апреля", "мая", "июня",
        "июля", "августа", "сентября", "октября", "ноября", "декабря",
    ]
    MONTHS_SHORT = [
        "", "янв", "фев", "мар", "апр", "май", "июн",
        "июл", "авг", "сен", "окт", "ноя", "дек",
    ]

    @app.template_filter("ru_date")
    def ru_date_filter(dt: datetime, fmt: str = "long") -> str:
        """Format date in Russian. fmt: 'long' = '20 марта 2025', 'short' = '20 мар 2025'."""
        if fmt == "short":
            return f"{dt.day} {MONTHS_SHORT[dt.month]} {dt.year}"
        return f"{dt.day} {MONTHS_FULL[dt.month]} {dt.year}"

    # CLI commands
    from cli import register_cli

    register_cli(app)

    # Create tables
    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
