__author__ = 'HansiHE'

from wtforms import ValidationError
import bcrypt
import re
from blueprints.auth.user_model import User
from blueprints.auth import current_user
from flask import abort
from functools import wraps


class LoginException(Exception):
    pass


def authenticate_user(username, password, message="Invalid username or password."):
    user = User.objects(name__iexact=username).first()
    if user is None:
        raise LoginException(message)
    if user.hash == bcrypt.hashpw(password, user.hash):
        return user
    else:
        raise LoginException(message)


def require_permissions(*permissions):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for permission in permissions:
                if not current_user.has_permission(permission):
                    abort(403)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def validate_username(username):
    if 2 <= len(username) <= 16 and re.match(r'^[A-Za-z0-9_]+$', username):
        return True
    return False
