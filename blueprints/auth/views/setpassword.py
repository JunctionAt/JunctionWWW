__author__ = 'HansiHE'

from wtforms import Form, PasswordField
from wtforms.validators import Required, Length, EqualTo
from flask_login import fresh_login_required, current_user, abort
from flask import request, flash, redirect, url_for, render_template
from werkzeug.datastructures import MultiDict

from .. import blueprint
import bcrypt


class SetPasswordForm(Form):
    password = PasswordField('New Password', [
        Required("You need to enter a password."),
        Length(min=8, message="The password is too short.")])
    password_match = PasswordField('Verify Password', [EqualTo('password', message="The passwords didn't match.")])


@blueprint.route("/profile/<string:name>/setpassword", methods=["GET", "POST"])
@fresh_login_required
def setpassword(name):
    if current_user.name != name:
        abort(404)

    form = SetPasswordForm(request.form)
    if request.method == "POST" and form.validate():
        print "wat"
        current_user.hash = bcrypt.hashpw(form.password.data, bcrypt.gensalt())
        current_user.save()
        flash('Your password has been changed.')
        return redirect(current_user.get_profile_url()), 303
    return render_template("setpassword.html", form=form, user=current_user)