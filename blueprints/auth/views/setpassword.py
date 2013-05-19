__author__ = 'HansiHE'

from wtforms import Form, PasswordField
from wtforms.validators import Required, Length, Optional
from flask_login import fresh_login_required, current_user
from flask import request, flash, redirect, url_for, render_template
from werkzeug.datastructures import MultiDict

from .. import blueprint
import bcrypt


class SetPasswordForm(Form):
    password = PasswordField('New Password', [Required(), Length(min=8)])
    password_match = PasswordField('Verify Password', [Optional()])


@blueprint.route("/setpassword", methods=["GET", "POST"])
@fresh_login_required
def setpassword():
    form = SetPasswordForm(MultiDict(request.json) or request.form)
    if request.method == "POST" and form.validate():
        current_user.hash = bcrypt.hashpw(form.password.data, bcrypt.gensalt())
        current_user.save()
        flash('Updated password')
        return redirect(url_for('player_profiles.edit_profile', ext='html')), 303
    return render_template("setpassword.html", form=form)