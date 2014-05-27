import re

from flask import request, render_template, redirect, url_for, flash, abort, session
from flask_login import login_user, login_required
from flask_wtf import Form
from wtforms import TextField, ValidationError
from wtforms.validators import *
from werkzeug.datastructures import MultiDict

from blueprints.auth.user_model import User
from blueprints.auth import current_user
from blueprints.api import apidoc
from .. import blueprint

from blueprints.auth.util import authenticate_user, LoginException

import base64
import binascii
from oath import accept_totp


class VerifyForm(Form):
    code = TextField('Verification Code', [Required("The verification code is required."),
                                           Length(min=6, max=6, message="Invalid code length.")])


@blueprint.route("/verify", defaults=dict(ext='html'), methods=("GET", "POST"))
def verify(ext):
    form = VerifyForm(MultiDict(request.json) or request.form)

    if request.method == "POST" and form.validate():
        # verify otp
        if session.get('tfa-logged-in', False) is not True:
            return redirect(url_for('auth.login')), 303

        user = User.objects(name=session['tfa-user']).next()

        ok, drift = accept_totp(format='dec6',
                                key=binascii.hexlify(base64.b32decode(user.tfa_secret)),
                                response=form.code.data,
                                drift=user.tfa_info.get('drift', 0))

        if not ok:
            form.errors['verify'] = ["Incorrect verification code."]
            return render_template('verify.html', form=form, title="Verify login")

        if login_user(user, remember=session['tfa-remember']):
            user.tfa_info['drift'] = drift
            user.save()
            if ext == 'json':
                return redirect("/"), 303
            flash("Logged in!", category="success")
            return redirect(request.args.get("next", '/'))

    if ext == 'json':
        if request.method == 'GET':
            abort(405)
        return login_required(lambda: (redirect("/"), 303))()

    return render_template("verify.html", form=form, title="Verify login")

