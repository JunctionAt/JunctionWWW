from flask import request, render_template, redirect, url_for, flash, session
from flask_login import login_user
from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import InputRequired, Length
import base64
import binascii
from oath import accept_totp

from models.user_model import User
from .. import blueprint


class VerifyForm(Form):
    code = StringField('Verification Code', [InputRequired("The verification code is required."),
                                             Length(min=6, max=6, message="Invalid code length.")])


@blueprint.route("/verify", methods=["GET", "POST"])
def verify():
    form = VerifyForm(request.form)

    if request.method == "POST" and form.validate():
        # verify otp
        if session.get('tfa-logged-in', False) is not True:
            return redirect(url_for('auth.login'))

        user = User.objects(name=session['tfa-user']).next()

        ok, drift = accept_totp(format='dec6',
                                key=binascii.hexlify(base64.b32decode(user.tfa_secret)),
                                response=form.code.data,
                                drift=user.tfa_info.get('drift', 0))

        if not ok:
            form.errors['verify'] = ["Incorrect verification code."]
            return render_template('verify.html', form=form, title="Verify Login")

        if login_user(user, remember=session['tfa-remember']):
            user.tfa_info['drift'] = drift
            user.save()
            flash("Logged in!", category="success")
            return redirect(request.args.get("next", '/'))

    return render_template("verify.html", form=form, title="Verify Login")

