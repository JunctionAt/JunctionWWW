__author__ = 'HansiHE'

import datetime
import bcrypt

from flask import request, render_template, redirect, url_for, jsonify, current_app, flash
from wtforms import Form, TextField, PasswordField, ValidationError
from wtforms.validators import *
from werkzeug.datastructures import MultiDict
from flask_login import login_user

from blueprints.auth.user_model import User, Token
from blueprints.api import apidoc
from .. import blueprint


class ActivationForm(Form):
    """Form to verify user by token."""

    token = TextField('Token', description='From ' + current_app.config.get('AUTH_SERVER', 'auth.junction.at'), validators=[ Required(), Length(min=6,max=6) ])
    password = PasswordField('Junction password', description='From step 1', validators=[ Required() ])

    def validate_password(self, field):
        try:
            setattr(
                self, 'token',
                Token.objects(token=self.token.data, expires__gte=datetime.datetime.utcnow()).order_by("-expires").first()
            )
            if not self.token or not bcrypt.hashpw(field.data, self.token.hash):
                raise ValidationError("Incorrect password.")
        except KeyError: pass

    def validate_token(self, field):
        if not self.token:
            raise ValidationError("Invalid token. Please note that activation tokens are only valid for 10 minutes.")


@apidoc(__name__, blueprint, '/activate.json', endpoint='activatetoken', defaults=dict(ext='json'), methods=('POST',))
def activatetoken_api(ext):
    """
    Used to activate an account with the token generated during the registration process. A client must send a ``password``, and ``token`` field.
    """


@blueprint.route("/activate", defaults=dict(ext='html'), methods=["GET", "POST"])
def activatetoken(ext):
    form = ActivationForm(MultiDict(request.json) or request.form)

    if request.method == "POST":

        if not form.validate():
            flash("Invalid token and/or password. Make sure its less then 10 minutes since you registered.")
            form = ActivationForm()
            #return render_template("verify.html", form=form, auth_server=current_app.config.get('AUTH_SERVER', 'auth.junction.at'))
            return redirect(url_for("auth.activatetoken", ext='html'))

        # noinspection PyArgumentList
        user = User(
            name=form.token.name,
            hash=form.token.hash,
            mail=form.token.mail,
            verified=True
        )
        user.save()
        login_user(user, remember=False)
        del form.token
        if ext == 'html': flash(u"Registration successful!")
        from blueprints.avatar import set_mc_face_as_avatar
        set_mc_face_as_avatar(user.name)
        return redirect("/"), 303
    if ext == 'json':
        return jsonify(
            fields=reduce(lambda errors, (name, field):
                          errors if not len(field.errors) else errors + [dict(name=name, errors=field.errors)],
                          form._fields.iteritems(),
                          list())), 400
    return render_template("verify.html", form=form, auth_server=current_app.config.get('AUTH_SERVER', 'auth.junction.at'))