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

from flask import (Flask, Blueprint, request, render_template, redirect, url_for, flash,
                   current_app, session, abort, jsonify)
import flask_login
from flask_login import (LoginManager, login_required as __login_required__, current_user,
                         login_user, logout_user, confirm_login, fresh_login_required, AnonymousUser)
from functools import wraps
from wtforms import Form, TextField, PasswordField, BooleanField, ValidationError
from wtforms.validators import *
from werkzeug.datastructures import MultiDict
from sqlalchemy.sql.operators import ColumnOperators
from sqlalchemy.orm.exc import *
import datetime
import random
import bcrypt
import re

from blueprints.base import mongo#db
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
    def get_id(self): return ""
    def is_authenticated(self): return True
    def is_anonymous(self): return True
    def is_active(self): return True

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

class LoginForm(Form):
    username = TextField('Minecraft Name', [ Required(), Length(min=2, max=16) ])
    password = PasswordField('Junction Password', validators=[ Required(), Length(min=8) ])
    remember = BooleanField('Stay logged in', [ Optional() ], default=True)
    def validate_password(self, field):
        if reduce(lambda errors, (name, field): errors or len(field.errors), self._fields.iteritems(), False):
            return
        try:
            self.user = User.objects(name=re.compile(self.username.data, re.IGNORECASE)).first()
            if self.user is None:
                raise KeyError
            if self.user.hash == bcrypt.hashpw(self.password.data, self.user.hash):
                return
        except KeyError: pass
        raise ValidationError('Invalid username or password.')

@blueprint.route("/login", defaults=dict(ext='html'), methods=("GET", "POST"))
def login(ext):
    form = LoginForm(MultiDict(request.json) or request.form)
    if request.method == "POST" and form.validate():
        if not form.user.verified:
            if ext == 'json': abort(403)
            flash(u"Please check your mail.")
            return redirect(url_for('auth.login', ext='html'))
        if login_user(form.user, remember=form.remember.data):
            if ext == 'json': return redirect("/"), 303
            flash("Logged in!")
            return redirect(request.args.get("next", '/'))
    if ext == 'json':
        if request.method == 'GET': abort(405)
        return login_required(lambda: (redirect("/"), 303))()
    return render_template("login.html", form=form)

@apidoc(__name__, blueprint, '/login.json', endpoint='login', defaults=dict(ext='json'), methods=('GET',))
def login_get_api(ext):
    """
    Send a GET request to /login.json if using HTTP Basic Auth. Use the returned cookie for subsequent requests.
    """

@apidoc(__name__, blueprint, '/login.json', endpoint='login', defaults=dict(ext='json'), methods=('POST',))
def login_post_api(ext):
    """
    If not logging in with HTTP Basic Auth, send a POST request including a ``username`` and ``password`` field.
    Use the returned cookie for subsequent requests.
    """

@blueprint.route("/reauth", methods=["GET", "POST"])
@login_required
def reauth():
    if request.method == "POST":
        confirm_login()
        flash(u"Reauthenticated.")
        return redirect(request.args.get("next", '/'))
    return render_template("reauth.html")


@blueprint.route("/logout", defaults=dict(ext='html'))
def logout(ext):
    logout_user()
    if ext == 'json': return "", 200
    flash("Logged out.")
    return redirect(url_for('auth.login', ext=ext))

@apidoc(__name__, blueprint, '/logout.json', endpoint='logout', defaults=dict(ext='json'))
def logout_api(ext):
    """
    Clears login session cookie.
    """

class RegistrationForm(Form):
    username = TextField('Minecraft Username', [ Required(), Length(min=2, max=16) ])
    mail = TextField('Email', description='Optional. Use for Gravatars.', validators=[ Optional(), Email() ])
    password = PasswordField('Password', description='Note: Does not need to be the same as your Minecraft password', validators=[ Required(), Length(min=8) ])
    password_match = PasswordField('Verify Password', [ Optional() ])
    def validate_username(self, field):
        if len(User.objects(name=re.compile(field.data, re.IGNORECASE))):
            raise ValidationError('This username is already registered.')

@apidoc(__name__, blueprint, '/register.json', endpoint='register', defaults=dict(ext='json'), methods=('POST',))
def register_api(ext):
    """
    Used to register a Junction account. The request must include a ``username`` and ``password`` field.
    An optional ``mail`` field may contain the users e-mail address.
    """

@blueprint.route("/register", defaults=dict(ext='html'), methods=["GET", "POST"])
def register(ext):
    form = RegistrationForm(MultiDict(request.json) or request.form)
    if request.method == "POST" and form.validate():
        token = Token(
            name=form.username.data,
            token=''.join(random.choice('0123456789abcdefghijklmnopqrstuvwxyz') for i in range(6)),
            hash=bcrypt.hashpw(form.password.data, bcrypt.gensalt()),
            mail=form.mail.data,
            ip=request.remote_addr,
            expires=datetime.datetime.utcnow() + datetime.timedelta(0, 10 * 60)
        ).save()
        return redirect(url_for('auth.activatetoken', ext=ext)), 303
    if ext == 'json':
        return jsonify(
            fields=reduce(lambda errors, (name, field):
                              errors if not len(field.errors) else errors + [dict(name=name, errors=field.errors)],
                          form._fields.iteritems(),
                          list())), 400
    if current_user.is_authenticated():
        return redirect(url_for('static_pages.landing_page'))
    return render_template("register.html", form=form)

class ActivationForm(Form):
    """Form to verify user by token."""

    token = TextField('Token', description='From ' + current_app.config.get('AUTH_SERVER', 'auth.junction.at'), validators=[ Required(), Length(min=6,max=6) ])
    password = PasswordField('Junction password', description='From step 1', validators=[ Required() ])

    def validate_password(self, field):
        try:
            setattr(
                self, 'token',
                Token.objects(token=self.token.data, expires__gte=datetime.datetime.utcnow()).order_by("-expires").first()
            )
            if not self.token or not bcrypt.hashpw(field.data, self.token.hash):
                raise ValidationError("Incorrect password.")
        except KeyError: pass

    def validate_token(self, field):
        if not self.token:
            raise ValidationError("Invalid token. Please note that activation tokens are only valid for 10 minutes.")

@apidoc(__name__, blueprint, '/activate.json', endpoint='activatetoken', defaults=dict(ext='json'), methods=('POST',))
def activatetoken_api(ext):
    """
    Used to activate an account with the token generated during the registration process. A client must send a ``password``, and ``token`` field.
    """

@blueprint.route("/activate", defaults=dict(ext='html'), methods=["GET", "POST"])
def activatetoken(ext):
    form = ActivationForm(MultiDict(request.json) or request.form)
    if not form.validate():
        flash("Invalid token and/or password. Make sure its less then 10 minutes since you registered.")
        form = ActivationForm()
        return render_template("verify.html", form=form, auth_server=current_app.config.get('AUTH_SERVER', 'auth.junction.at'))
    if request.method == "POST":
        # noinspection PyArgumentList
        user = User(
            name=form.token.name,
            hash=form.token.hash,
            mail=form.token.mail,
            verified=True
        )
        user.save()
        login_user(user, remember=False)
        del form.token
        if ext == 'html': flash(u"Registration successful!")
        from blueprints.avatar import set_mc_face_as_avatar
        set_mc_face_as_avatar(user.name)
        return redirect("/"), 303
    if ext == 'json':
        return jsonify(
            fields=reduce(lambda errors, (name, field):
                              errors if not len(field.errors) else errors + [dict(name=name, errors=field.errors)],
                          form._fields.iteritems(),
                          list())), 400
    return render_template("verify.html", form=form, auth_server=current_app.config.get('AUTH_SERVER', 'auth.junction.at'))

@apidoc(__name__, blueprint, '/token/<player>.json', defaults=dict(ext='json'))
@login_required
def get_token(player, ext):
    """
    Used by staff to get the activation token for ``player``.
    """

    if not current_user.has_permission("auth.get_token"):
        abort(403)

    try:
        return jsonify(token=Token.objects(name=player, expires__gte=datetime.datetime.utcnow()).order_by("-expires").first().token)
    except NoResultFound:
        abort(404)

class SetPasswordForm(Form):
    password = PasswordField('New Password', [ Required(), Length(min=8) ])
    password_match = PasswordField('Verify Password', [ Optional() ])

@blueprint.route("/setpassword", methods=["GET", "POST"])
@fresh_login_required
def setpassword():
    form = SetPasswordForm(MultiDict(request.json) or request.form)
    if request.method == "POST" and form.validate():
        current_user.hash = bcrypt.hashpw(form.password.data, bcrypt.gensalt())
        current_user.save()
        flash('Updated password')
        return redirect(url_for('player_profiles.edit_profile', ext='html')), 303
    return render_template("setpassword.html", form=form)