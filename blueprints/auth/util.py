__author__ = 'HansiHE'

import bcrypt
import re
from flask import abort
from functools import wraps

from models.user_model import User
from blueprints.auth import current_user



# class Login(object):
#     def __init__(self, name_field="username", message="Invalid Password"):
#         self.name_field = name_field
#         self.message = message
#
#     def __call__(self, form, field):
#         self.username_field = getattr(form, self.name_field)
#         self.username_field.validate()
#         if reduce(lambda errors, (name, field): errors or len(field.errors), form._fields.iteritems(), False):
#             return
#         try:
#             form.user = User.objects(name=re.compile(self.username_field.data, re.IGNORECASE)).first()
#
#             if form.user is None:
#                 raise KeyError
#             if form.user.hash == bcrypt.hashpw(field.data, form.user.hash):
#                 return
#
#         except KeyError:
#             pass
#         raise ValidationError('Invalid username or password.')


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

        # def validate_password(self, field):
        #     if reduce(lambda errors, (name, field): errors or len(field.errors), self._fields.iteritems(), False):
        #         return
        #     try:
        #         self.user = User.objects(name=re.compile(self.username.data, re.IGNORECASE)).first()
        #         if self.user is None:
        #             raise KeyError
        #         if self.user.hash == bcrypt.hashpw(self.password.data, self.user.hash):
        #             return
        #     except KeyError:
        #         pass
        #     raise ValidationError('Invalid username or password.')


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