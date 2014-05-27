__author__ = 'HansiHE'

import bcrypt
import re
import datetime
from flask import abort
from functools import wraps

from models.user_model import User, ConfirmedUsername
from blueprints.auth import current_user


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


def check_authenticated_ip(ip, uuid=None, username=None):

    time_check = datetime.datetime.utcnow() - datetime.timedelta(minutes=15)

    opt = dict()
    opt.update(dict(uuid=uuid) if uuid is not None else dict())
    opt.update(dict(username__iexact=username) if username is not None else dict())

    return ConfirmedUsername.objects(ip=str(ip), created__gt=time_check, **opt).order_by('-created').first()


def add_authenticated_ip(username, uuid, ip):
    confirmed = ConfirmedUsername(ip=ip, username=username, uuid=uuid)
    confirmed.save()