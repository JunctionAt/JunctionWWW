__author__ = 'HansiHE'

from .. import blueprint, login_required
from flask import request, flash, redirect, render_template, session, current_app, abort
from flask_login import confirm_login, login_fresh, current_user, user_needs_refresh, login_url


@blueprint.route("/reauth", methods=["GET", "POST"])
@login_required
def reauth():
    print login_fresh()
    if request.method == "POST":
        confirm_login()
        session.modified = True  # Damnit flask
        flash(u"Reauthenticated.")
        return redirect(request.args.get("next", '/'))
    return render_template("reauth.html")