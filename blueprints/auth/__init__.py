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
from flask_login import (LoginManager, login_required as __login_required__,
                         login_user, logout_user, confirm_login, fresh_login_required)
from flask.ext.principal import Permission, RoleNeed
from functools import wraps
from wtforms import Form, TextField, PasswordField, ValidationError
from wtforms.validators import *
from sqlalchemy.orm.exc import *
import datetime
import random
import bcrypt
import re

from blueprints.base import db
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

def login_required(f):
    """
    This is a custom version of the flask_login decorator that will accept HTTP Basic Auth or
    fall back on the regular login_required provided by flask_login.
    """
    
    @wraps(f)
    def decorated(*args, **kwargs):
        if not flask_login.current_user.is_authenticated():
            try:
                auth = request.authorization
                user = db.session.query(User).filter(User.name==auth.username).first()
                if not user or not user.hash == bcrypt.hashpw(auth.password, user.hash) or \
                        not login_user(user, remember=False, force=True):
                    raise Exception()
            except:
                return __login_required__(f)(*args, **kwargs)
        return f(*args, **kwargs)
    return decorated

@login_manager.user_loader
def load_user(id):
    return load_user_name(id)

login_manager.setup_app(current_app, add_context_processor=True)

def load_user_field(field, value):
    #result = db.session.execute("SELECT name, hash, mail, registered, verified FROM users WHERE %s=:value;"%field, dict(value=value)).fetchone()
    return db.session.query(User).filter(getattr(User,field)==value).first()

def load_user_name(name):
    return load_user_field("name", name)
	
def wpass():
    flash(u"The username or password was incorrect.")
    return redirect(url_for('auth.login', ext='html'))
	
@blueprint.route("/login", defaults=dict(ext='html'), methods=("GET", "POST"))
def login(ext):
    if request.method == "POST" and ("username" in request.form or "username" in request.json) and \
            ("password" in request.form or "password" in request.json):
	username = (request.json or request.form)["username"]
	password = (request.json or request.form)["password"]
        user = db.session.query(User).filter(User.name==username).first()
        if user and user.hash == bcrypt.hashpw(password, user.hash):
            if not user.verified:
                if ext == 'json': abort(403)
                flash(u"Please check your mail.")
                return redirect(url_for('auth.login', ext='html'))
            remember = request.form.get("remember", "no") == "yes"
            if login_user(load_user_name(username), remember=remember):
                if ext == 'json': return redirect(url_for('player_profiles.show_profile',
                                                          player=username, ext=ext)), 303
                flash("Logged in!")
                return redirect(request.args.get("next", url_for('auth.controlpanel')))
        if ext == 'html':
            return wpass()
    if ext == 'json':
        return login_required(lambda: (redirect(url_for('player_profiles.show_profile',
                                                        player=flask_login.current_user.name, ext=ext)), 303))()
    return render_template("login.html")

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
	return redirect(request.args.get("next", url_for('auth.controlpanel')))
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
    username = TextField('Username', [ Required(), Length(min=2, max=16) ])
    mail = TextField('Email', description='Optional. Use for Gravatars.', validators=[ Optional(), Email() ])
    password = PasswordField('Password', [ Required() ])
    password_match = PasswordField('Verify Password', [ Optional() ])
    def validate_username(form, field):
        if db.session.query(User).filter(User.name==field.data).count():
            raise ValidationError('This username is already registered.')

@apidoc(__name__, blueprint, '/register.json', endpoint='register', defaults=dict(ext='json'), methods=('POST',))
def register_api(ext):
    """
    Used to register a Junction account. The request must include a ``username`` and ``password`` field.
    An optional ``mail`` field may contain the users e-mail address.
    """

@blueprint.route("/register", defaults=dict(ext='html'), methods=["GET", "POST"])
def register(ext):
    form = RegistrationForm(request.json or request.form)
    if request.method == "POST" and form.validate():
        token = Token()
        token.token = ''.join(random.choice('0123456789abcdefghijklmnopqrstuvwxyz') for i in range(6))
        token.hash = bcrypt.hashpw(form.password.data, bcrypt.gensalt())
        token.mail = form.mail.data
        token.ip = request.remote_addr
        token.expires = datetime.datetime.utcnownow + 10 * 60
        db.session.add(token)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            abort(500)
        return redirect(url_for('auth.activatetoken', ext=ext)), 303
    if ext == 'json':
        return jsonify(
            fields=reduce(lambda errors, (name, field):
                              errors if not len(field.errors) else errors + [dict(name=name, errors=field.errors)],
                          form._fields.iteritems(),
                          list())), 400
    return render_template("register.html", form=form)

class ActivationForm(Form):
    """Form to verify user by token."""
    
    token = TextField('Token', [ Required(), Length(min=6,max=6) ])
    password = PasswordField('Password', [ Required() ])
    
    def validate_password(form, field):
        try:
            setattr(
                form, 'token',
                db.session.query(Token) \
                    .filter(Token.token==form._fields['token'].data) \
                    .filter(Token.expires>=datetime.datetime.utcnow).one())
            if not bcrypt.hashpw(field.data, token.hash):
                raise ValidationError("Incorrect password.")
        except KeyError: pass
        except NoResultFound: pass
            
    def validate_token(form, field):
        if not hasattr(form, 'token'):
            raise ValidationError("Invalid token. Please note that activation tokens are only valid for 10 minutes.")

@apidoc(__name__, blueprint, '/activate.json', endpoint='activatetoken', defaults=dict(ext='json'), methods=('POST',))
def activatetoken_api(ext):
    """
    Used to activate an account with the token generated during the registration process. A client must send a ``password``, and ``token`` field.
    """

@blueprint.route("/activate", defaults=dict(ext='html'), methods=["GET", "POST"])
def activatetoken(ext):
    form = ActivationForm(request.json or request.form)
    if request.method == "POST" and form.validate():
        user = User()
        user.name = form.token.name
        user.hash = form.token.password
        user.mail = form.token.mail
        db.session.add(user)
        db.session.remove(form.token)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            abort(500)
        if ext == 'html': flash(u"Registration sucessful! You can now log in with your account.")
        return redirect(url_for('auth.login'), ext=ext)
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
    Used by staff to get the activation cookie for ``player``.
    """

    with Permission(RoleNeed('get_token')).require(403):
        try:
            return jsonify(token=db.session.query(Token) \
                               .filter(Token.name==player) \
                               .filter(Token.expires>=datetime.datetime.utcnow).one().token)
        except NoResultFound:
            abort(404)

@blueprint.route("/control", methods=["GET", "POST"])
@fresh_login_required
def controlpanel():
    if request.method == "POST":
        if request.form['newpassword']:
            hashed = bcrypt.hashpw(request.form['newpassword'], bcrypt.gensalt())
            db.session.execute('UPDATE users SET hash=:hash WHERE name=:name;', dict(hash=hashed, name=flask_login.current_user.name))
            try:
                db.session.commit()
            except:
                db.session.rollback()
                abort(500)
            flash('Updated password')
            return render_template("controlpanel.html")
    return render_template("controlpanel.html")
