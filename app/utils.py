from __future__ import annotations

import secrets
from datetime import datetime
from decimal import Decimal
from urllib.parse import urljoin, urlparse

from flask import current_app, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer


def generate_order_number() -> str:
    stamp = datetime.utcnow().strftime("%y%m%d%H%M%S")
    return f"MO{stamp}{secrets.randbelow(900) + 100:03d}"


def is_safe_redirect_target(target: str | None) -> bool:
    if not target:
        return False
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return ref_url.scheme == test_url.scheme and ref_url.netloc == test_url.netloc


def is_safe_path_or_url(value: str | None) -> bool:
    if not value:
        return False

    candidate = value.strip()
    if candidate.lower().startswith("javascript:"):
        return False
    if candidate.startswith("/"):
        return True

    parsed = urlparse(candidate)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def password_reset_serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])


def generate_password_reset_token(account_type: str, email: str) -> str:
    serializer = password_reset_serializer()
    return serializer.dumps(
        {
            "account_type": account_type,
            "email": email,
        },
        salt="password-reset",
    )


def verify_password_reset_token(token: str, max_age: int = 60 * 30) -> dict[str, str] | None:
    serializer = password_reset_serializer()
    try:
        payload = serializer.loads(token, salt="password-reset", max_age=max_age)
    except (BadSignature, SignatureExpired):
        return None

    if isinstance(payload, str):
        return {"account_type": "registered", "email": payload}
    if isinstance(payload, dict):
        account_type = str(payload.get("account_type", "")).strip()
        email = str(payload.get("email", "")).strip()
        if account_type and email:
            return {"account_type": account_type, "email": email}
    return None


def money(value: Decimal | float | int | str) -> str:
    return f"{Decimal(value):,.2f}"
