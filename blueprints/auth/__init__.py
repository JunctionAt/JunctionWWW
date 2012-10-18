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
for multiple requests is not recommended. The server will attempt to verify your credentilas
on every Basic Auth request, which will cause the request to take longer than
normal to complete. Only use Basic Auth once to obtain a session cookie if you are making
multiple requests.
"""

from flask import (Flask, Blueprint, request, render_template, redirect, url_for, flash,
                   current_app, session, abort)
import flask_login
from flask_login import (LoginManager, login_required as __login_required__,
                            login_user, logout_user, confirm_login, fresh_login_required)
from functools import wraps
from wtforms import Form, TextField, PasswordField, ValidationError
from wtforms.validators import *
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
login_manager.refresh_view = "reauth"

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

def redirectd(path):
    return redirect(subpath+path)

def load_user_field(field, value):
    #result = db.session.execute("SELECT name, hash, mail, registered, verified FROM users WHERE %s=:value;"%field, dict(value=value)).fetchone()
    return db.session.query(User).filter(getattr(User,field)==value).first()

def load_user_name(name):
    return load_user_field("name", name)
	
def wpass():
    flash(u"The username or password was incorrect.")
    return redirectd("/login")
	
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
                return redirect("/login")
            remember = request.form.get("remember", "no") == "yes"
            if login_user(load_user_name(username), remember=remember):
                if ext == 'json': return redirect(url_for('player_profiles.show_profile',
                                                          player=username, ext=ext)), 303
                flash("Logged in!")
                return redirect(request.args.get("next", "/control"))
        if ext == 'html':
            return wpass()
    if ext == 'json':
        return login_required(lambda: (redirect(url_for('player_profiles.show_profile',
                                                        player=flask_login.current_user.name, ext=ext)), 303))()
    return render_template("login.html")

@blueprint.route("/reauth", methods=["GET", "POST"])
@login_required
def reauth():
    if request.method == "POST":
	confirm_login()
	flash(u"Reauthenticated.")
	return redirect(request.args.get("next") or "/control")
    return render_template("reauth.html")


@apidoc(__name__, blueprint, '/logout.json', endpoint='logout', defaults=dict(ext='json'))
def logout_api(ext):
    """
    Clears login session cookie.
    """

@blueprint.route("/logout", defaults=dict(ext='html'))
def logout(ext):
    logout_user()
    if ext == 'json': return "", 200
    flash("Logged out.")
    return redirect(url_for('auth.login', ext=ext))

@apidoc(__name__, blueprint, '/register.json', endpoint='register', defaults=dict(ext='json'), methods=('POST',))
def register_api(ext):
    """
    Used to register a Junction account. The request must include a ``username`` and ``password`` field.
    An optional ``mail`` field may contain the users e-mail address.
    """

class RegistrationForm(Form):
    username = TextField('Username', [ Required(), Length(min=2, max=16) ])
    mail = TextField('Email', description='Optional. Use for Gravatars.', validators=[ Optional(), Email() ])
    password = PasswordField('Password', [ Required() ])
    password_match = PasswordField('Verify Password', [ Optional() ])
    def validate_username(form, field):
        if db.session.query(User).filter(User.name==field.data).count():
            raise ValidationError('This username is already registered.')

@blueprint.route("/register", defaults=dict(ext='html'), methods=["GET", "POST"])
def register(ext):
    form = RegistrationForm(request.json or request.form)
    if request.method == "POST" and form.validate():
        token = Token()
        token.token = ''.join(random.choice('0123456789abcdefghijklmnopqrstuvwxyz') for i in range(6))
        token.hash = bcrypt.hashpw(form.password.data, bcrypt.gensalt())
        token.mail = form.mail.data
        token.ip = request.remote_addr
        token.expires = datetime.datetime.now + 10 * 60
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

@blueprint.route("/activate", methods=["GET", "POST"])
def activatetoken():
    if request.method == "POST":
        result = db.session.execute("SELECT name, hash, mail FROM tokens WHERE token=:token AND expires>NOW();", dict(token=str(request.form['token']))).fetchone()
        if result is None:
            flash(u"Validation token invalid. Make sure you entered the right one, and that you didn't use more then 10 minutes since the registration.")
            return render_template("register.html")
        db.session.execute("DELETE FROM tokens WHERE token=:token;", dict(token=(request.form['token'])))
        if not db.session.execute("INSERT INTO users (name, hash, mail, registered, verified) VALUES (:name, :hash, :mail, NOW(), TRUE);",
                               dict(name=result[0], hash=result[1], mail=result[2])):
            flash(u"An internal error occured. If this continues happening, please contact staff at contact@junction.at")
            return redirect("/login")
        try:
            db.session.commit()
        except:
            db.session.rollback()
            abort(500)
        flash(u"Registration sucessful! You can now log in with your account.")
        return redirect("/login")
    else:
	return render_template("verify.html", auth_server=current_app.config.get('AUTH_SERVER', 'auth.junction.at'))

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
