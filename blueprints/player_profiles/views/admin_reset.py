from flask_wtf import Form
from wtforms import HiddenField
from flask_login import fresh_login_required, current_user, abort, login_required
from flask import request, flash, redirect, url_for, render_template
import random
import bcrypt

from models.user_model import User
from .. import blueprint
from blueprints.settings.views import add_settings_pane, settings_panels_structure


class ResetForm(Form):
    who = HiddenField()


@blueprint.route("/reset/<what>", methods=["POST"])
@login_required
def reset(what):
    if not current_user.has_permission('reset.{}'.format(what)):
        abort(403)

    form = ResetForm(request.form)
    if form.validate():
        user = User.objects(name=form.who.data).first()
        if user is None:
            abort(401)
        if what == 'password':
            password = ''.join(random.choice('0123456789abcdefghijklmnopqrstuvxyzABCDEFGHIJKLMNOPQRSTUVWXYZ') for i in range(16))
            user.hash = bcrypt.hashpw(password, bcrypt.gensalt())
            user.save()
            return render_template('profile_reset_password_successful.html', user=user, password=password)
        elif what == 'tfa':
            user.tfa = False
            user.tfa_secret = ''
            user.save()
            return render_template('profile_reset_tfa_successful.html', user=user)
        else:
            abort(401)

    return redirect(user.get_profile_url()), 303
