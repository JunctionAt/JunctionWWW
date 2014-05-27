__author__ = 'HansiHE'

from flask import request, flash, redirect, render_template
from flask_login import confirm_login, current_user
from flask_wtf import Form
from wtforms import PasswordField
from wtforms.validators import InputRequired, Length

from .. import blueprint, login_required
from blueprints.auth.util import authenticate_user, LoginException


class ReAuthForm(Form):
    password = PasswordField('Junction Password',
                             [InputRequired("A password is required."),
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
            return render_template("reauth.html", form=form)

        confirm_login()  # Note: Cookies are a bit glitchy with the dev domains it seems, don't panic

        flash("Reauthenticated.", category="success")
        return redirect(request.args.get("next", '/'))
    return render_template("reauth.html", form=form, title="Refresh Login")
