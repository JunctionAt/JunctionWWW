__author__ = 'HansiHE'

from .. import alts
from flask import render_template


@alts.route("/alts/graph/")
def graph_lookup_view():
    return render_template("graph_view.html")