from __future__ import annotations

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from sqlalchemy import or_

from app.account_policy import normalize_musiconline_email
from app.extensions import db
from app.forms import ForgotPasswordForm, LoginForm, RegisterForm, ResetPasswordForm
from app.models import AdminUser, RegisteredUser
from app.seed import ensure_core_data
from app.utils import (
    generate_password_reset_token,
    is_safe_redirect_target,
    verify_password_reset_token,
)


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def wants_json_response() -> bool:
    requested_with = request.headers.get("X-Requested-With", "").lower()
    if requested_with == "xmlhttprequest":
        return True

    best = request.accept_mimetypes.best
    if best != "application/json":
        return False

    return request.accept_mimetypes[best] >= request.accept_mimetypes["text/html"]


def first_form_error(form) -> str | None:
    for errors in form.errors.values():
        if errors:
            return errors[0]
    return None


def append_field_error(field, message: str) -> None:
    if message not in field.errors:
        field.errors.append(message)


def find_accounts_by_identifier(identifier: str):
    normalized = identifier.strip().lower()
    accounts = []
    for model in (AdminUser, RegisteredUser):
        account = db.session.scalar(
            db.select(model).where(or_(model.username == normalized, model.email == normalized))
        )
        if account is not None:
            accounts.append(account)
    return accounts


def find_account_by_email(account_type: str, email: str):
    normalized = email.strip().lower()
    if account_type == "admin":
        return db.session.scalar(db.select(AdminUser).where(AdminUser.email == normalized))
    if account_type == "registered":
        return db.session.scalar(db.select(RegisteredUser).where(RegisteredUser.email == normalized))
    return None


# >>> API ENTRY: GET/POST /auth/register - user registration <<<
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        redirect_url = url_for("dashboard.home")
        if wants_json_response():
            return jsonify({"ok": True, "redirect_url": redirect_url})
        return redirect(redirect_url)

    form = RegisterForm()
    if form.validate_on_submit():
        ensure_core_data()

        username = form.username.data.strip().lower()
        email = normalize_musiconline_email(form.email.data)
        field_errors: dict[str, list[str]] = {}

        username_taken = any(
            db.session.scalar(db.select(model).where(or_(model.username == username, model.email == username)))
            is not None
            for model in (AdminUser, RegisteredUser)
        )
        email_taken = any(
            db.session.scalar(db.select(model).where(or_(model.email == email, model.username == email))) is not None
            for model in (AdminUser, RegisteredUser)
        )

        if username_taken:
            message = "That username is already in use."
            append_field_error(form.username, message)
            field_errors["username"] = [message]
        if email_taken:
            message = "That email address is already in use."
            append_field_error(form.email, message)
            field_errors["email"] = [message]

        if field_errors:
            if wants_json_response():
                return (
                    jsonify(
                        {
                            "ok": False,
                            "title": "Account not created",
                            "message": "That username or email is already in use.",
                            "errors": field_errors,
                            "fields": list(field_errors.keys()),
                        }
                    ),
                    409,
                )
            flash("That username or email is already in use.", "error")
        else:
            user = RegisteredUser(
                username=username,
                email=email,
                display_name=form.display_name.data.strip(),
                is_retailer=form.is_retailer.data,
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            redirect_url = url_for("dashboard.home")
            flash("Account created successfully.", "success")
            if wants_json_response():
                return jsonify({"ok": True, "redirect_url": redirect_url})
            return redirect(redirect_url)

    if request.method == "POST" and wants_json_response():
        return (
            jsonify(
                {
                    "ok": False,
                    "title": "Check your details",
                    "message": first_form_error(form) or "Please complete the required fields.",
                    "errors": form.errors,
                    "fields": [field for field, errors in form.errors.items() if errors],
                }
            ),
            422,
        )

    return render_template("auth/register.html", form=form)


# >>> API ENTRY: GET/POST /auth/login - user login <<<
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        redirect_url = url_for("dashboard.home")
        if wants_json_response():
            return jsonify({"ok": True, "redirect_url": redirect_url})
        return redirect(redirect_url)

    form = LoginForm()
    if form.validate_on_submit():
        identifier = form.username.data.strip().lower()
        accounts = find_accounts_by_identifier(identifier)
        user = next((account for account in accounts if account.check_password(form.password.data)), None)

        if user is None:
            if wants_json_response():
                return (
                    jsonify(
                        {
                            "ok": False,
                            "title": "Sign in failed",
                            "message": "Incorrect username or password.",
                            "fields": ["username", "password"],
                        }
                    ),
                    401,
                )
            flash("Invalid credentials.", "error")
        elif not user.is_active:
            if wants_json_response():
                return (
                    jsonify(
                        {
                            "ok": False,
                            "title": "Account unavailable",
                            "message": "This account is disabled. Please contact the administrator.",
                            "fields": ["username"],
                        }
                    ),
                    403,
                )
            flash("This account is disabled. Please contact the administrator.", "error")
        else:
            login_user(user, remember=form.remember.data)
            next_url = request.args.get("next")
            redirect_url = next_url if is_safe_redirect_target(next_url) else url_for("dashboard.home")
            flash("Welcome back.", "success")
            if wants_json_response():
                return jsonify({"ok": True, "redirect_url": redirect_url})
            return redirect(redirect_url)

    if request.method == "POST" and wants_json_response():
        return (
            jsonify(
                {
                    "ok": False,
                    "title": "Check your details",
                    "message": first_form_error(form) or "Please enter your username and password.",
                    "errors": form.errors,
                    "fields": [field for field, errors in form.errors.items() if errors],
                }
            ),
            422,
        )

    return render_template("auth/login.html", form=form)


# >>> API ENTRY: GET/POST /auth/forgot-password - password reset request <<<
@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if current_user.is_authenticated:
        redirect_url = url_for("dashboard.home")
        if wants_json_response():
            return jsonify({"ok": True, "redirect_url": redirect_url})
        return redirect(redirect_url)

    form = ForgotPasswordForm()
    reset_link = None
    target_user = None

    if form.validate_on_submit():
        identifier = form.identifier.data.strip().lower()
        accounts = find_accounts_by_identifier(identifier)
        target_user = accounts[0] if accounts else None

        if target_user is not None:
            token = generate_password_reset_token(target_user.account_type, target_user.email)
            reset_link = url_for("auth.reset_password", token=token)

        if wants_json_response():
            payload = {
                "ok": True,
                "title": "Request processed",
                "message": "If the account exists, a reset link is ready below.",
                "result": {
                    "visible": True,
                    "found": target_user is not None,
                    "title": (
                        f"{target_user.display_name} can now reset the password."
                        if target_user is not None
                        else "No matching account was found."
                    ),
                    "message": (
                        "Open the secure reset page below."
                        if target_user is not None
                        else "Try another username or email if a reset link is still needed."
                    ),
                    "link_url": reset_link or "",
                    "link_label": "Open Reset Password",
                },
            }
            return jsonify(payload)

        flash("If the account exists, a reset link is ready below.", "info")

    if request.method == "POST" and wants_json_response():
        return (
            jsonify(
                {
                    "ok": False,
                    "title": "Check your details",
                    "message": first_form_error(form) or "Please enter your username or email.",
                    "errors": form.errors,
                    "fields": [field for field, errors in form.errors.items() if errors],
                }
            ),
            422,
        )

    return render_template(
        "auth/forgot_password.html",
        form=form,
        reset_link=reset_link,
        target_user=target_user,
    )


# >>> API ENTRY: GET/POST /auth/reset-password/<token> - password reset form <<<
@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token: str):
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.home"))

    payload = verify_password_reset_token(token)
    if payload is None:
        flash("The reset link is invalid or has expired.", "error")
        return redirect(url_for("auth.forgot_password"))

    user = find_account_by_email(payload["account_type"], payload["email"])
    if user is None:
        flash("The reset link is no longer valid.", "error")
        return redirect(url_for("auth.forgot_password"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Password updated successfully. Please sign in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html", form=form, target_user=user)


# >>> API ENTRY: POST /auth/logout - user logout <<<
@auth_bp.post("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash("Signed out successfully.", "info")
    return redirect(url_for("public.home"))
