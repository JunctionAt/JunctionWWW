__author__ = 'HansiHE'

from flask import Blueprint


blueprint = Blueprint('settings', __name__, template_folder='templates')

from views import main, email, reddit
