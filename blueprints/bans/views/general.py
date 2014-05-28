from flask import render_template

from .. import bans


@bans.route('/a/')
def a_front():
    return render_template('a_front.html', title="Anathema")
