from __future__ import annotations

import re

from wtforms.validators import ValidationError


MUSICONLINE_EMAIL_SUFFIX = "@musiconline.com"
DEFAULT_ACCOUNT_PASSWORD = "123456"

EMAIL_LOCAL_PART_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]{2,63}$")


def normalize_musiconline_email(email: str | None) -> str:
    return (email or "").strip().lower()


def validate_musiconline_email(_, field) -> None:
    normalized = normalize_musiconline_email(field.data)

    if not normalized.endswith(MUSICONLINE_EMAIL_SUFFIX):
        raise ValidationError("Email must use the xxx@musiconline.com format.")

    local_part = normalized[: -len(MUSICONLINE_EMAIL_SUFFIX)]
    if not local_part or normalized == local_part:
        raise ValidationError("Email must use the xxx@musiconline.com format.")
    if not EMAIL_LOCAL_PART_PATTERN.match(local_part):
        raise ValidationError("Use 3-64 letters, numbers, dots, hyphens, or underscores before @musiconline.com.")

    field.data = normalized
