__author__ = 'HansiHE'

from flask import Blueprint


blueprint = Blueprint('calendar', __name__, template_folder='templates')

from views import calendar_view