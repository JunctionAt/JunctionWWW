__author__ = 'HansiHE'

from flask import request, render_template, redirect, flash
from flask_login import login_user
from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import *

from blueprints.auth import current_user
from .. import blueprint
from blueprints.auth.util import authenticate_user, LoginException


class LoginForm(Form):
    username = StringField('Minecraft Name', [InputRequired("A username is required."),
                                              Length(min=2, max=16, message="Invalid username length.")])
    password = PasswordField('Junction Password', validators=[InputRequired("A password is required."),
                                                              Length(min=8, message="The password is too short.")])
    remember = BooleanField('Remember Me', [Optional()], default=True)


@blueprint.route("/login", methods=("GET", "POST"))
def login():
    if current_user.is_authenticated():
        return redirect(request.args.get("next", '/'))

    form = LoginForm(request.form)

    if request.method == "POST" and form.validate():
        try:
            user = authenticate_user(form.username.data, form.password.data)
        except LoginException, e:
            form.errors["login"] = [e.message]
            return render_template("login.html", form=form, title="Login")

        #if not user.verified:
        #    flash(u"Please check your mail.")
        #    return redirect(url_for('auth.login', ext='html'))

        if login_user(user, remember=form.remember.data):
            flash("Logged in!", category="success")
            return redirect(request.args.get("next", '/'))

    return render_template("login.html", form=form, title="Login")
