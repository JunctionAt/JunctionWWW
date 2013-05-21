__author__ = 'HansiHE'

from .. import blueprint, login_required
from flask import request, flash, redirect, render_template, session, current_app, abort
from flask_login import confirm_login, login_fresh, current_user, user_needs_refresh, login_url
from wtforms import Form, PasswordField
from wtforms.validators import Required, Length
from blueprints.auth.util import authenticate_user, LoginException


class ReAuthForm(Form):
    password = PasswordField('Junction Password', validators=[Required("A password is required."),
                                                              Length(min=8, message="The password is too short.")])


@blueprint.route("/reauth", methods=["GET", "POST"])
@login_required
def reauth():
    form = ReAuthForm(request.form)
    if request.method == "POST" and form.validate():
        try:
            user = authenticate_user(current_user.name, form.password.data)
        except LoginException, e:
            form.errors["login"] = [e.message]
            return render_template("login.html", form=form)

        confirm_login()  # Note: Cookies are a bit glitchy with the dev domains it seems, don't panic

        flash(u"Reauthenticated.")
        return redirect(request.args.get("next", '/'))
    return render_template("reauth.html", form=form)