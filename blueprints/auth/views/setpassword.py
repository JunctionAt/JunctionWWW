from flask_wtf import Form
from wtforms import PasswordField
from wtforms.validators import InputRequired, Length, EqualTo
from flask_login import fresh_login_required, current_user, abort, login_required
from flask import request, flash, redirect, url_for, render_template
import random
import bcrypt

from models.user_model import User
from .. import blueprint
from blueprints.settings.views import add_settings_pane, settings_panels_structure


class SetPasswordForm(Form):
    password = PasswordField('New Password', [
        InputRequired("You need to enter a password."),
        Length(min=8, message="The password is too short.")])
    password_match = PasswordField('Verify Password', [EqualTo('password', message="The passwords didn't match.")])


@blueprint.route("/settings/setpassword", methods=["GET", "POST"])
@fresh_login_required
def setpassword():
    form = SetPasswordForm(request.form)
    if request.method == "POST" and form.validate():
        current_user.hash = bcrypt.hashpw(form.password.data, bcrypt.gensalt())
        current_user.save()
        flash('Your password has been changed.', category="success")
        return redirect(current_user.get_profile_url()), 303
    return render_template("setpassword_settings_pane.html", form=form, user=current_user, settings_panels_structure=settings_panels_structure, title="Change Password - Account - Settings")

add_settings_pane(lambda: url_for('auth.setpassword'), "Account", "Change Password", menu_id="setpassword")
