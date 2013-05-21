__author__ = 'HansiHE'

import re
import random
import datetime
import bcrypt

from flask import request, render_template, redirect, url_for, jsonify
from wtforms import Form, TextField, PasswordField, ValidationError
from wtforms.validators import *
from werkzeug.datastructures import MultiDict

from blueprints.auth.user_model import User, Token
from blueprints.api import apidoc
from .. import blueprint, current_user


class RegistrationForm(Form):
    username = TextField('Minecraft Username', [ Required(), Length(min=2, max=16) ])
    mail = TextField('Email', description='Optional. Use for Gravatars.', validators=[ Optional(), Email() ])
    password = PasswordField('Password', description='Note: Does not need to be the same as your Minecraft password', validators=[ Required(), Length(min=8) ])
    password_match = PasswordField('Verify Password', [EqualTo('password', message="The passwords need to match.")])
    def validate_username(self, field):
        if len(User.objects(name=re.compile(field.data, re.IGNORECASE))):
            raise ValidationError('This username is already registered.')


@apidoc(__name__, blueprint, '/register.json', endpoint='register', defaults=dict(ext='json'), methods=('POST',))
def register_api(ext):
    """
    Used to register a Junction account. The request must include a ``username`` and ``password`` field.
    An optional ``mail`` field may contain the users e-mail address.
    """


@blueprint.route("/register", defaults=dict(ext='html'), methods=["GET", "POST"])
def register(ext):
    form = RegistrationForm(MultiDict(request.json) or request.form)
    if request.method == "POST" and form.validate():
        token = Token(
            name=form.username.data,
            token=''.join(random.choice('0123456789abcdefghijklmnopqrstuvwxyz') for i in range(6)),
            hash=bcrypt.hashpw(form.password.data, bcrypt.gensalt()),
            mail=form.mail.data,
            ip=request.remote_addr,
            expires=datetime.datetime.utcnow() + datetime.timedelta(0, 10 * 60)
        ).save()
        return redirect(url_for('auth.activatetoken', ext=ext)), 303
    if ext == 'json':
        return jsonify(
            fields=reduce(lambda errors, (name, field):
                          errors if not len(field.errors) else errors + [dict(name=name, errors=field.errors)],
                          form._fields.iteritems(),
                          list())), 400
    if current_user.is_authenticated():
        return redirect(url_for('static_pages.landing_page'))
    return render_template("register.html", form=form)