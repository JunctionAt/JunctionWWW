__author__ = 'HansiHE'

from flask import Blueprint, render_template, send_file

blueprint = Blueprint('donations', __name__,
                         template_folder='templates')

import ipn

@blueprint.route('/donate')
def donate():
    funds_current = 80
    funds_target = 300
    return render_template(
        'donate_new.html',
        funds_percentage=round((funds_current/float(funds_target))*100, 1),
        funds_target=funds_target,
        funds_current=funds_current
        )