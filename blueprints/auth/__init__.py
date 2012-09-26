from flask import Flask, Blueprint, request, render_template, redirect, url_for, flash, current_app
from flask_login import (LoginManager, current_user, login_required,
                            login_user, logout_user, UserMixin, AnonymousUser,
                            confirm_login, fresh_login_required)
import random
import bcrypt
import re

class User(UserMixin):
    def __init__(self, name, hash, mail, registered, verified):
        self.id = name
        self.name = name
        self.hash = hash
        self.mail = mail
        self.registered = registered
        self.verified = verified

    def is_active(self):
        return self.verified


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
    return load_user_name(id)

login_manager.setup_app(current_app)

def redirectd(path):
    return redirect(subpath+path)

def open_db():
    #return MySQLdb.connect(host='localhost', user='loginweb', db='auth')
    return current_app.config['ENGINE'].connect()

def load_user_field(field, value):
    db = open_db()
    with db.begin() as cursor:
        result = db.execute("SELECT name, hash, mail, registered, verified FROM users WHERE "+field+"=%s;", (value)).fetchone()
        #db.close()
        if result is None:
            return None
        return User(result[0], result[1], result[2], result[3], result[4])

def load_user_name(name):
    return load_user_field("name", name)
	
def wpass():
    flash(u"The username or password was incorrect.")
    return redirectd("/login")
	
@blueprint.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST" and "username" in request.form and "password" in request.form:
	username = request.form["username"]
	password = request.form["password"]
        db = open_db()
	with db.begin() as cursor:
            result = db.execute("SELECT name, hash, verified FROM users WHERE name=%s;", (username)).fetchone()
            if result != None:
                hashed = bcrypt.hashpw(password, result[1])
                if hashed == result[1]:
                    if result[2] == False:
                        flash(u"Please check your mail.")
                        return redirect("/login")
                    remember = request.form.get("remember", "no") == "yes"
                    if login_user(load_user_name(username), remember=remember):
                        flash("Logged in!")
                        return redirect("/control")
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
            db = open_db()
            with db.begin() as cursor:
                db.execute("INSERT INTO tokens (token, name, hash, mail, ip, expires) VALUES (%s, %s, %s, %s, %s, now()+INTERVAL 10 MINUTE);", playertoken, request.form['username'], hashed, request.form['mail'], request.remote_addr)
            db.close()
            return redirect("/activate")
    else:
        return render_template("register.html")

@blueprint.route("/activate", methods=["GET", "POST"])
def activatetoken():
    if request.method == "POST":
	db = open_db()
	with db.begin() as cursor:
            result = db.execute("SELECT name, hash, mail FROM tokens WHERE token=%s AND expires>NOW();", str(request.form['token'])).fetchone()
            if result is None:
                flash(u"Validation token invalid. Make sure you entered the right one, and that you didn't use more then 10 minutes since the registration.")
                return render_template("register.html")
            db.execute("DELETE FROM tokens WHERE token=%s;", (request.form['token']))
            if not db.execute("INSERT INTO users (name, hash, mail, registered, verified) VALUES (%s, %s, %s, NOW(), TRUE);", result[0], result[1], result[2]):
                flash(u"An internal error occured. If this continues happening, please contact staff at contact@junction.at")
                return redirect("/login")
            flash(u"Registration sucessful! You can now log in with your account.")
            return redirect("/login")
    else:
	return render_template("verify.html")

@blueprint.route("/control", methods=["GET", "POST"])
@fresh_login_required
def controlpanel():
    if request.method == "POST":
        db = open_db()
        with db.begin() as cursor:
            if request.form['newpassword']:
                hashed = bcrypt.hashpw(request.form['newpassword'], bcrypt.gensalt())
                db.execute('UPDATE users SET hash=%s WHERE name=%s;', (hashed, current_user.name))
                flash('Updated password')
                return render_template("controlpanel.html")
    return render_template("controlpanel.html")
	
