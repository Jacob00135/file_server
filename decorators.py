from functools import wraps
from flask import abort
from flask_login import current_user


def anonymous_forbidden(f):
    @wraps(f)
    def func(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(403)
        return f(*args, **kwargs)
    return func
