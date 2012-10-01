from flask import Flask, Blueprint, request, render_template, redirect, url_for, flash, current_app
from flask_login import (LoginManager, current_user, login_required,
                            login_user, logout_user, AnonymousUser,
                            confirm_login, fresh_login_required)
import random
import bcrypt
import re

from blueprints.base import session
from blueprints.auth.user_model import User

class Anonymous(AnonymousUser):
    name = u"Anonymous"

subpath = ''

mailregex = re.compile("[^@]+@[^@]+\.[^@]+")

blueprint = Blueprint('auth', __name__, template_folder='templates', static_folder='static', static_url_path='/auth/static')

login_manager = LoginManager()

login_manager.anonymous_user = Anonymous
login_manager.login_view = "login"
login_manager.login_message = u"Please log in to access this page."
login_manager.refresh_view = "reauth"

@login_manager.user_loader
def load_user(id):
    user = load_user_name(id)
    if user:
        User._user = user
    return user

login_manager.setup_app(current_app, add_context_processor=True)

def redirectd(path):
    return redirect(subpath+path)

def load_user_field(field, value):
    #result = session.execute("SELECT name, hash, mail, registered, verified FROM users WHERE %s=:value;"%field, dict(value=value)).fetchone()
    return session.query(User).filter(getattr(User,field)==value).first()

def load_user_name(name):
    return load_user_field("name", name)
	
def wpass():
    flash(u"The username or password was incorrect.")
    return redirectd("/login")
	
@current_app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST" and "username" in request.form and "password" in request.form:
	username = request.form["username"]
	password = request.form["password"]
        #result = session.execute("SELECT name, hash, verified FROM users WHERE name=:username;", dict(username=username)).fetchone()
        user = session.query(User).filter(User.name==username).first()
        if user:
            hashed = bcrypt.hashpw(password, user.hash)
            if hashed == user.hash:
                if not user.verified:
                    flash(u"Please check your mail.")
                    return redirect("/login")
                remember = request.form.get("remember", "no") == "yes"
                if login_user(load_user_name(username), remember=remember):
                    flash("Logged in!")
                    return redirect(request.args.get("next", "/control"))
                else:
                    return wpass()
            else:
                return wpass()
    return render_template("login.html")

@blueprint.route("/reauth", methods=["GET", "POST"])
@login_required
def reauth():
    if request.method == "POST":
	confirm_login()
	flash(u"Reauthenticated.")
	return redirect(request.args.get("next") or "/control")
    return render_template("reauth.html")


@blueprint.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.")
    return redirect("/login")

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
            session.execute("INSERT INTO tokens (token, name, hash, mail, ip, expires) VALUES (:token, :name, :hash, :mail, :ip, now()+INTERVAL 10 MINUTE);",
                            dict(token=playertoken,
                                 name=request.form['username'],
                                 hash=hashed,
                                 mail=request.form['mail'],
                                 ip=request.remote_addr))
            session.commit()
            return redirect("/activate")
    else:
        return render_template("register.html")

@blueprint.route("/activate", methods=["GET", "POST"])
def activatetoken():
    if request.method == "POST":
        result = session.execute("SELECT name, hash, mail FROM tokens WHERE token=:token AND expires>NOW();", dict(token=str(request.form['token']))).fetchone()
        if result is None:
            flash(u"Validation token invalid. Make sure you entered the right one, and that you didn't use more then 10 minutes since the registration.")
            return render_template("register.html")
        session.execute("DELETE FROM tokens WHERE token=:token;", dict(token=(request.form['token'])))
        session.commit()
        if not session.execute("INSERT INTO users (name, hash, mail, registered, verified) VALUES (:name, :hash, :mail, NOW(), TRUE);",
                               dict(name=result[0], hash=result[1], mail=result[2])):
            flash(u"An internal error occured. If this continues happening, please contact staff at contact@junction.at")
            return redirect("/login")
        session.commit()
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
            session.execute('UPDATE users SET hash=:hash WHERE name=:name;', dict(hash=hashed, name=current_user.name))
            session.commit()
            flash('Updated password')
            return render_template("controlpanel.html")
    return render_template("controlpanel.html")
	
