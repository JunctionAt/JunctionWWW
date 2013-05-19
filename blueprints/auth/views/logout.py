__author__ = 'HansiHE'

from .. import blueprint
from flask_login import logout_user
from flask import flash, redirect, url_for
from blueprints.api import apidoc

@blueprint.route("/logout", defaults=dict(ext='html'))
def logout(ext):
    logout_user()
    if ext == 'json': return "", 200
    flash("Logged out.")
    return redirect(url_for('auth.login', ext=ext))


@apidoc(__name__, blueprint, '/logout.json', endpoint='logout', defaults=dict(ext='json'))
def logout_api(ext):
    """
    Clears login session cookie.
    """