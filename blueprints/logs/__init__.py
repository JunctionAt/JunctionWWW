import flask
from flask import Blueprint, abort
from flask.ext.login import login_required
from flask.ext.principal import PermissionDenied

from blueprints.roles.permissions import show_logs_permission


logs = Blueprint(__name__, 'logs', template_folder="templates")

@logs.route('/logs')
@login_required
def show_logs():
    try:
        with show_logs_permission.require():
            return render_template('show_logs.html', logs=[])
    except PermissionDenied:
        abort(403)
