from __future__ import annotations

from functools import wraps

from flask import abort
from flask_login import current_user, login_required


def permission_required(code: str):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped_view(*args, **kwargs):
            if not current_user.has_permission(code):
                abort(403)
            return view_func(*args, **kwargs)

        return wrapped_view

    return decorator
