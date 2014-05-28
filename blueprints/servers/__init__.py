__author__ = 'williammck'

from flask import Blueprint

blueprint = Blueprint('servers', __name__, template_folder='templates')

from views import view_servers