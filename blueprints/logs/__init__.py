import flask
from flask import Blueprint, abort
from flask.ext.login import login_required
from flask.ext.principal import Permission, PermissionDenied, RoleNeed


logs = Blueprint('logs', __name__, template_folder="templates")

@logs.route('/logs')
@login_required
def show_logs():
    try:
        with Permission(RoleNeed('show_logs')).require():
            return render_template('show_logs.html', logs=[])
    except PermissionDenied:
        abort(403)
