from blueprints import uuid_utils

__author__ = 'HansiHE'

from flask import render_template, request, abort, redirect, url_for, flash
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Email, InputRequired, Length, EqualTo, Optional
import bcrypt

from .. import blueprint
from models.user_model import User
from models.player_model import MinecraftPlayer
from blueprints.auth import login_required, current_user
from blueprints.auth.util import check_authenticated_ip


@blueprint.route('/register/')
def register_start():
    if current_user.is_authenticated():
        flash("You are already logged in. Log out to register another account.", category="alert")
        return redirect(url_for('static_pages.landing_page'))
    return render_template('register_1.html', title="Step 1 - Register")


class RegistrationForm(Form):
    mail = StringField("Email", validators=[Optional(), Email()])
    password = PasswordField("Password", validators=[
        InputRequired("Please enter a password."),
        Length(min=8, message="The password needs to be longer then 6 characters.")])
    password_repeat = PasswordField("Repeat Password", validators=[
        EqualTo('password', "The passwords must match.")])
    submit = SubmitField("Register")


@blueprint.route('/register/<string:username>/', methods=['GET', 'POST'])
def register_pool(username):
    if current_user.is_authenticated():
        flash("You are already logged in. Log out to register another account.", category="alert")
        return redirect(url_for('static_pages.landing_page'))

    if User.objects(name=username).first() is not None:
        flash("This user is already registered.", category="alert")
        return redirect(url_for('auth.login'))

    #Is verified
    auth_check = check_authenticated_ip(request.remote_addr, username=username)
    if auth_check:
        form = RegistrationForm(request.form)

        if request.method == "GET":
            return render_template('register_3.html', username=username, form=form, title="Step 3 - Register")

        elif request.method == "POST":
            if form.validate():
                uuid = auth_check.uuid.hex
                player = MinecraftPlayer.find_or_create_player(uuid, auth_check.username)
                user = User(
                    name=username,
                    hash=bcrypt.hashpw(form.password.data, bcrypt.gensalt()),
                    mail=form.mail.data,
                    minecraft_player=player)
                user.save()
                flash("Registration complete!", category="success")
                return redirect(url_for('auth.login'))
            return render_template('register_3.html', username=username, form=form, title="Step 3 - Register")

    #Is not verified
    else:
        if request.method == "GET":
            return render_template('register_2.html', username=username, title="Waiting... - Step 2 - Register")
        else:
            abort(405)


@blueprint.route('/api/check_auth/<string:username>/')
def check_authenticated_req(username):
    return "YES" if check_authenticated_ip(request.remote_addr, username=username) else "NO"


@blueprint.route('/ip')
def get_ip():
    return request.remote_addr
