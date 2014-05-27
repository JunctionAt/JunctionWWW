__author__ = 'HansiHE'

from flask import Blueprint

blueprint = Blueprint('player_profiles', __name__, template_folder='templates')

from views import profile_views, send_pm