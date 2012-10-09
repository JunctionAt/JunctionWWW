"""
Authorization
-------------

Cookie based login method. HTTP Basic Auth is also accepted, allowing you to bypass the login and cookie.
"""

from flask import Flask, Blueprint, request, render_template, redirect, url_for, flash, current_app, session
import flask_login
from flask_login import (LoginManager, login_required as __login_required__,
                            login_user, logout_user, confirm_login, fresh_login_required)
from functools import wraps
import random
import bcrypt
import re

from blueprints.base import db
from blueprints.auth.user_model import User
from blueprints.api import apidoc

subpath = ''

mailregex = re.compile("[^@]+@[^@]+\.[^@]+")

blueprint = Blueprint('auth', __name__, template_folder='templates', static_folder='static', static_url_path='/auth/static')

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
                    raise Exception
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
	
@apidoc(__name__, blueprint, '/login.json', endpoint='login', defaults=dict(ext='json'), methods=('POST',))
def login_api(ext):
    """
    Login with ``username`` and ``passwords`` fields. Use the cookie in the response header for subsequent requests.
    """

@blueprint.route("/login", defaults=dict(ext='html'), methods=("GET", "POST"))
def login(ext):
    if request.method == "POST" and ("username" in request.form or "username" in request.json) and ("password" in request.form or "password" in request.json):
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
                if ext == 'json': return redirect(url_for('player_profiles.show_profile', player=username, ext=ext)), 303
                flash("Logged in!")
                return redirect(request.args.get("next", "/control"))
        if ext == 'html':
            return wpass()
    if ext == 'json': abort(403)
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

@blueprint.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
	if "username" in request.form and "password1" in request.form and "mail" in request.form:
            if len(request.form.get('username', '')) <2:
                flash(u"The Minecraft username was too short.")
                return redirect("/register")
            if len(request.form['username']) > 16:
		flash(u"The Minecraft username was too long.")
		return redirect("/register")
            if not mailregex.match(request.form['mail']):
                flash(u"Please enter a valid email adress.")
                return redirect("/register")
            playertoken = ''.join(random.choice('0123456789abcdefghijklmnopqrstuvwxyz') for i in range(6))
            hashed = bcrypt.hashpw(request.form['password1'], bcrypt.gensalt())
            db.session.execute("INSERT INTO tokens (token, name, hash, mail, ip, expires) VALUES (:token, :name, :hash, :mail, :ip, now()+INTERVAL 10 MINUTE);",
                            dict(token=playertoken,
                                 name=request.form['username'],
                                 hash=hashed,
                                 mail=request.form['mail'],
                                 ip=request.remote_addr))
            try:
                db.session.commit()
            except:
                db.session.rollback()
                abort(500)
            return redirect("/activate")
    else:
        return render_template("register.html")

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
