from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateField,
    DecimalField,
    IntegerField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, EqualTo, Length, NumberRange, Optional, ValidationError

from app.account_policy import validate_musiconline_email
from app.utils import is_safe_path_or_url


def validate_safe_path_or_url(_, field) -> None:
    if not field.data:
        return
    if not is_safe_path_or_url(field.data):
        raise ValidationError("Please enter a root-relative path or an http/https URL.")


class LoginForm(FlaskForm):
    username = StringField("Username or Email", validators=[DataRequired(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=128)])
    remember = BooleanField("Remember this device")
    submit = SubmitField("Sign In")


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=64)])
    display_name = StringField("Display Name", validators=[DataRequired(), Length(min=2, max=64)])
    email = StringField("Email", validators=[DataRequired(), Length(max=120), validate_musiconline_email])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=128)])
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match.")],
    )
    is_retailer = BooleanField("Register as a retailer")
    submit = SubmitField("Create Account")


class ForgotPasswordForm(FlaskForm):
    identifier = StringField("Username or Email", validators=[DataRequired(), Length(max=120)])
    submit = SubmitField("Generate Reset Link")


class ResetPasswordForm(FlaskForm):
    password = PasswordField("New Password", validators=[DataRequired(), Length(min=6, max=128)])
    confirm_password = PasswordField(
        "Confirm New Password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match.")],
    )
    submit = SubmitField("Reset Password")


class ProductForm(FlaskForm):
    title = StringField("Vinyl Title", validators=[DataRequired(), Length(max=120)])
    artist = StringField("Artist", validators=[DataRequired(), Length(max=120)])
    format_type = SelectField(
        "Format",
        choices=[("album", "Album"), ("single", "Single"), ("ep", "EP")],
        validators=[DataRequired()],
    )
    category_id = SelectField("Category", coerce=int, validators=[DataRequired()])
    release_date = DateField("Release Date", validators=[Optional()], format="%Y-%m-%d")
    price = DecimalField("Listed Price (RMB)", validators=[DataRequired(), NumberRange(min=0)], places=2)
    stock = IntegerField("Copies Available", validators=[DataRequired(), NumberRange(min=0, max=9999)])
    image_url = StringField(
        "Cover Image URL",
        validators=[Optional(), Length(max=255), validate_safe_path_or_url],
    )
    description = TextAreaField("Listing Description", validators=[DataRequired(), Length(min=20, max=2000)])
    submit = SubmitField("Save Listing")
