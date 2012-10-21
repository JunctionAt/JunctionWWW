import flask
from flask import Blueprint, abort
from flask.ext.login import login_required
from flask.ext.principal import Permission, RoleNeed


logs = Blueprint('logs', __name__, template_folder="templates")

@logs.route('/logs')
@login_required
def show_logs():
    with Permission(RoleNeed('show_logs')).require(403):
        return render_template('show_logs.html', logs=[])
