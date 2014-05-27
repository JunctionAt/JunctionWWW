__author__ = 'HansiHE'

from flask import request, render_template, redirect, url_for, flash, abort, session
from flask_login import login_user, login_required
from flask_wtf import Form
from wtforms import TextField, PasswordField, BooleanField, ValidationError
from wtforms.validators import *
from werkzeug.datastructures import MultiDict

import bcrypt
from blueprints.auth.user_model import User
from blueprints.auth import current_user
from blueprints.api import apidoc
from .. import blueprint

from blueprints.auth.util import authenticate_user, LoginException


class LoginForm(Form):
    username = TextField('Minecraft Name', [InputRequired("A username is required."),
                                            Length(min=2, max=16, message="Invalid username length.")])
    password = PasswordField('Junction Password', validators=[InputRequired("A password is required."),
                                                              Length(min=8, message="The password is too short.")])
    remember = BooleanField('Remember Me', [Optional()], default=True)


@blueprint.route("/login", defaults=dict(ext='html'), methods=("GET", "POST"))
def login(ext):
    if current_user.is_authenticated():
        return redirect(request.args.get("next", '/'))

    if session.get('tfa-logged-in', False) == True:
        del session['tfa-logged-in']
        del session['tfa-user']
        del session['tfa-remember']

    form = LoginForm(MultiDict(request.json) or request.form)

    if request.method == "POST" and form.validate():
        try:
            user = authenticate_user(form.username.data, form.password.data)
        except LoginException, e:
            form.errors["login"] = [e.message]
            return render_template("login.html", form=form, title="Login")

        if user.tfa:
            session['tfa-logged-in'] = True
            session['tfa-user'] = user.name
            session['tfa-remember'] = form.remember.data
            return redirect(url_for('auth.verify', next=request.args.get('next', '/'))), 303

        if login_user(user, remember=form.remember.data):
            if ext == 'json':
                return redirect("/"), 303
            flash("Logged in!", category="success")
            return redirect(request.args.get("next", '/'))

    if ext == 'json':
        if request.method == 'GET':
            abort(405)
        return login_required(lambda: (redirect("/"), 303))()

    return render_template("login.html", form=form, title="Login")


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
