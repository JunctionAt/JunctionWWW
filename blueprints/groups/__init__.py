__author__ = 'HansiHE'

from flask import Blueprint


blueprint = None


def get_blueprint():
    global blueprint
    if blueprint is None:
        blueprint = Blueprint('groups', __name__, template_folder='templates')

    return blueprint