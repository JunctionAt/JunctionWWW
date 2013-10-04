__author__ = 'HansiHE'

from wtforms import Form, PasswordField
from wtforms.validators import Required, Length, EqualTo
from flask_login import fresh_login_required, current_user, abort
from flask import request, flash, redirect, url_for, render_template
from werkzeug.datastructures import MultiDict
from blueprints.auth.user_model import User
import random

from .. import blueprint
import bcrypt
from blueprints.settings.views import add_settings_pane, settings_panels_structure


class SetPasswordForm(Form):
    password = PasswordField('New Password', [
        Required("You need to enter a password."),
        Length(min=8, message="The password is too short.")])
    password_match = PasswordField('Verify Password', [EqualTo('password', message="The passwords didn't match.")])


@blueprint.route("/settings/setpassword", methods=["GET", "POST"])
@fresh_login_required
def setpassword():
    form = SetPasswordForm(request.form)
    if request.method == "POST" and form.validate():
        current_user.hash = bcrypt.hashpw(form.password.data, bcrypt.gensalt())
        current_user.save()
        flash('Your password has been changed.')
        return redirect(current_user.get_profile_url()), 303
    return render_template("setpassword_settings_pane.html", form=form, user=current_user, settings_panels_structure=settings_panels_structure, title="Settings - Account - Change Password")

add_settings_pane(lambda: url_for('auth.setpassword'), "Account", "Change Password", menu_id="setpassword")


@blueprint.route("/profile/<string:name>/resetpassword")
def reset_password(name):
    if not current_user.has_permission('auth.reset_password'):
        abort(403)

    password = ''.join(random.choice('0123456789abcdefghijklmnopqrstuvxyzABCDEFGHIJKLMNOPQRSTUVWXYZ') for i in range(16))

    user = User.objects(name=name).first()
    user.hash = bcrypt.hashpw(password, bcrypt.gensalt())
    user.save()

    return password
