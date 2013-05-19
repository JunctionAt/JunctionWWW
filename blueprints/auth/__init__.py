"""
Authentication and Registration
-------------------------------

Some API resources are only accessible to authenicated users.
A user needs a registered and verified Junction account to access these resources.
The best way to maintain authentication during your session is to request a session cookie
that you use for all requests. To get a session cookie, use the /login.json endpoint.
The /login.json endpoint will accept HTTP Basic Auth or request body data containing your
username and password.

`Note:` All restricted resources will accept HTTP Basic Auth, however, using HTTP Basic Auth
for multiple requests is not recommended. The server will attempt to verify your password
on every Basic Auth request, which will cause the request to take longer than
normal to complete. Only use Basic Auth once to obtain a session cookie if you are making
multiple requests.
"""

from functools import wraps
import datetime
import re

from flask import ( Blueprint, request, current_app, abort, jsonify)
from flask_login import (LoginManager, login_required as __login_required__, current_user,
                         login_user, AnonymousUser)

import bcrypt
from blueprints.auth.user_model import User, Token
from blueprints.api import apidoc


subpath = ''

mailregex = re.compile("[^@]+@[^@]+\.[^@]+")

blueprint = Blueprint('auth', __name__, template_folder='templates',
                      static_folder='static', static_url_path='/auth/static')

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = u"Please log in to access this page."
login_manager.refresh_view = "auth.reauth"


# noinspection PyShadowingBuiltins
@login_manager.user_loader
def user_loader(id):
    return load_user(id)


# noinspection PyShadowingBuiltins
def load_user(id):
    if id == ApiUser().get_id() and current_app.config.get('API', False):
        return ApiUser()
    user = User.objects(name=re.compile(id, re.IGNORECASE)).first()
    if user is None:
        return None
    user.load_perms()
    return user

login_manager.init_app(current_app, add_context_processor=True)


class Anon(AnonymousUser):

    def has_permission(self, perm_node):
        return False

login_manager.anonymous_user = Anon


class ApiUser:
    def get_id(self):
        return ""

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return True

    def is_active(self):
        return True


def login_required(f):
    """
    This is a custom version of the flask_login decorator that will accept HTTP Basic Auth or
    fall back on the regular login_required provided by flask_login.
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated():
            try:
                auth = request.authorization
                user = User.objects(name=re.compile(auth.username, re.IGNORECASE)).first()
                if not user or not user.hash == bcrypt.hashpw(auth.password, user.hash) or \
                        not login_user(user, remember=False, force=True):
                    raise Exception()
            except:
                if current_app.config.get('API', False):
                    login_user(ApiUser())
                else:
                    if request.path[-5:] == '.json': abort(403)
                    return __login_required__(f)(*args, **kwargs)
        return f(*args, **kwargs)
    return decorated

from views import login, logout, register, activate, reauth, setpassword, administrative