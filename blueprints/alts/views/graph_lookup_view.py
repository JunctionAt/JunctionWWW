__author__ = 'HansiHE'

from .. import alts
from flask import render_template


@alts.route("/alts/graph/")
@alts.route("/alts/graph/<string:player>")
def graph_lookup_view(player=None):
    return render_template("graph_view.html", preload=[player] if player else [])