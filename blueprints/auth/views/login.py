__author__ = 'HansiHE'

import re

from flask import request, render_template, redirect, url_for, flash, abort
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
    username = TextField('Minecraft Name', [Required("A username is required."),
                                            Length(min=2, max=16, message="Invalid username length.")])
    password = PasswordField('Junction Password', validators=[Required("A password is required."),
                                                              Length(min=8, message="The password is too short.")])
    remember = BooleanField('Remember Me', [Optional()], default=True)

    #validate_password = Login(message="Invalid username or password.")

    # def validate_password(self, field):
    #     if reduce(lambda errors, (name, field): errors or len(field.errors), self._fields.iteritems(), False):
    #         return
    #     try:
    #         self.user = User.objects(name=re.compile(self.username.data, re.IGNORECASE)).first()
    #         if self.user is None:
    #             raise KeyError
    #         if self.user.hash == bcrypt.hashpw(self.password.data, self.user.hash):
    #             return
    #     except KeyError:
    #         pass
    #     raise ValidationError('Invalid username or password.')


from app import csrf
@csrf.exempt
@blueprint.route("/login", defaults=dict(ext='html'), methods=("GET", "POST"))
def login(ext):
    if current_user.is_authenticated():
        return redirect(request.args.get("next", '/'))

    form = LoginForm(MultiDict(request.json) or request.form)

    if request.method == "POST" and form.validate():
        try:
            user = authenticate_user(form.username.data, form.password.data)
        except LoginException, e:
            form.errors["login"] = [e.message]
            return render_template("login.html", form=form)

        #if not user.verified:
        #    if ext == 'json': abort(403)
        #    flash(u"Please check your mail.")
        #    return redirect(url_for('auth.login', ext='html'))

        if login_user(user, remember=form.remember.data):
            if ext == 'json':
                return redirect("/"), 303
            flash("Logged in!")
            return redirect(request.args.get("next", '/'))

    if ext == 'json':
        if request.method == 'GET':
            abort(405)
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