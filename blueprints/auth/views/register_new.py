__author__ = 'HansiHE'

from .. import blueprint
from flask import render_template, request, abort, redirect, url_for, flash
from ..user_model import ConfirmedUsername
from blueprints.auth import login_required, current_user
from blueprints.auth.user_model import User
from wtforms import Form, TextField, PasswordField, SubmitField, ValidationError
from wtforms.validators import Email, Required, Length, EqualTo, Optional
import re
import bcrypt


@blueprint.route('/register/')
def register_start():
    if current_user.is_authenticated():
        flash("You are already logged in. Log out to register another account.")
        return redirect('/')
    return render_template('register_1.html')


class RegistrationForm(Form):
    mail = TextField("Email", validators=[Optional(), Email()])
    password = PasswordField("Password", validators=[
        Required("Please enter a password."),
        Length(min=8, message="The password needs to be longer then 6 characters.")])
    password_repeat = PasswordField("Repeat Password", validators=[
        EqualTo('password', "The passwords must match.")])
    submit = SubmitField("Register")


@blueprint.route('/register/<string:username>/', methods=['GET', 'POST'])
def register_pool(username):
    if current_user.is_authenticated():
        flash("You are already logged in. Log out to register another account.")
        return redirect('/')

    if User.objects(name=username).first() is not None:
        flash("This user is already registered.")
        return redirect(url_for('auth.login'))

    #Is verified
    if check_authenticated(username, request.remote_addr):
        form = RegistrationForm(request.form)

        if request.method == "GET":
            return render_template('register_3.html', username=username, form=form)

        elif request.method == "POST":
            if form.validate():
                user = User(
                    name=username,
                    hash=bcrypt.hashpw(form.password.data, bcrypt.gensalt()),
                    mail=form.mail.data)
                user.save()
                flash("Registration complete!")
                return redirect(url_for('auth.login'))
            return render_template('register_3.html', username=username, form=form)

    #Is not verified
    else:
        if request.method == "GET":
            return render_template('register_2.html', username=username)
        else:
            abort(405)


@blueprint.route('/api/check_auth/<string:username>/')
def check_authenticated_req(username):
    return "YES" if check_authenticated(username, request.remote_addr) else "NO"


def check_authenticated(username, ip):
    return ConfirmedUsername.objects(ip=str(ip), username__iexact=username).first() is not None


@login_required
@blueprint.route('/api/confirm_auth/<string:username>/<string:ip>/')
def confirm_auth_req(username, ip):
    if not current_user.has_permission('auth.confirm_auth'):
        abort(403)
    confirm_auth(username, ip)
    return "Success"


def confirm_auth(username, ip):
    confirmed = ConfirmedUsername(ip=ip, username=username)
    confirmed.save()


@blueprint.route('/ip')
def get_ip():
    return request.remote_addr