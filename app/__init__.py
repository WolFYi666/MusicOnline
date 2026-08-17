from __future__ import annotations

import os
from datetime import datetime

import click
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import current_user, logout_user
from sqlalchemy import func

from config import Config
from app.extensions import csrf, db, login_manager
from app.models import AdminUser, CartItem, Category, Order, OrderItem, Product, RegisteredUser
from app.schema import ensure_schema_updates
from app.seed import ensure_core_data, ensure_demo_data
from app.utils import money


def create_app() -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please sign in to continue."
    login_manager.login_message_category = "info"
    login_manager.session_protection = "strong"

    register_blueprints(app)
    register_error_handlers(app)
    register_request_guards(app)
    register_template_helpers(app)
    register_cli(app)

    return app


@login_manager.user_loader
def load_user(user_id: str) -> AdminUser | RegisteredUser | None:
    if not user_id or ":" not in user_id:
        return None

    account_type, raw_id = user_id.split(":", 1)
    if not raw_id.isdigit():
        return None

    if account_type == "admin":
        return db.session.get(AdminUser, int(raw_id))
    if account_type == "registered":
        return db.session.get(RegisteredUser, int(raw_id))
    return None


def register_blueprints(app: Flask) -> None:
    from app.blueprints.auth import auth_bp
    from app.blueprints.commerce import commerce_bp
    from app.blueprints.dashboard import dashboard_bp
    from app.blueprints.public import public_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(commerce_bp)
    app.register_blueprint(dashboard_bp)


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(403)
    def forbidden(_):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(_):
        return render_template("errors/404.html"), 404


def register_request_guards(app: Flask) -> None:
    @app.before_request
    def enforce_active_session():
        if not current_user.is_authenticated or current_user.is_active:
            return None
        logout_user()
        flash("This account is inactive. Please contact the administrator.", "error")
        if request.endpoint == "auth.login":
            return None
        return redirect(url_for("auth.login"))


def register_template_helpers(app: Flask) -> None:
    @app.context_processor
    def inject_globals():
        bag_item_count = 0
        if current_user.is_authenticated and not current_user.is_admin:
            bag_item_count = db.session.scalar(
                db.select(func.coalesce(func.sum(CartItem.quantity), 0)).where(CartItem.buyer_id == current_user.id)
            ) or 0
        return {
            "current_year": datetime.utcnow().year,
            "bag_item_count": bag_item_count,
        }

    app.add_template_filter(money, "money")


def register_cli(app: Flask) -> None:
    @app.cli.command("init-db")
    @click.option(
        "--with-showcase",
        "--with-demo",
        "with_showcase",
        is_flag=True,
        help="Create tables and load the musicOnline demo catalog.",
    )
    def init_db_command(with_showcase: bool) -> None:
        db.create_all()
        ensure_schema_updates()
        ensure_core_data()
        if with_showcase:
            ensure_demo_data()
        click.echo("Database initialized.")
