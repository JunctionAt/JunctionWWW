__author__ = 'HansiHE'

from .. import bans
from flask import render_template, abort
from flask_login import current_user
from blueprints.bans.ban_model import Ban
from blueprints.bans.appeal_model import Appeal
from blueprints.auth import login_required
import math

@bans.route('/a/')
def a_front():
    return render_template('a_front.html', title="Anathema")
