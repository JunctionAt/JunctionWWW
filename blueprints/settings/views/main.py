__author__ = 'HansiHE'

from flask import render_template
from .. import blueprint
from blueprints.auth import login_required
from . import settings_panels_structure


@blueprint.route('/settings/')
@login_required
def settings_main():
    return render_template('settings_base.html', settings_panels_structure=settings_panels_structure)