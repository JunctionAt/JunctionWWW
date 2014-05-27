__author__ = 'HansiHE'

from .. import alts
from flask import render_template, abort
from blueprints.auth import current_user, login_required
from flask_wtf.csrf import generate_csrf


@alts.route("/alts/graph/")
@alts.route("/alts/graph/<string:player>")
@login_required
def graph_lookup_view(player=None):
    if not current_user.has_permission('alts.graph'):
        abort(403)

    return render_template("graph_view.html", preload=[player] if player else [], csrf_token=generate_csrf())
