__author__ = 'HansiHE'

from flask import Blueprint, render_template

blueprint = Blueprint('staff', __name__, template_folder='templates')

from views import staff_overview