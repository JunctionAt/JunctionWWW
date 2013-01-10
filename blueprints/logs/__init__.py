import flask
from flask import Blueprint, abort, render_template
from blueprints.auth import login_required
from flask_login import current_user

logs = Blueprint('logs', __name__, template_folder="templates")

@logs.route('/logs')
@login_required
def show_logs():
    if not current_user.has_permission("logs"):
        abort(503)

    return render_template('show_logs.html', logs=[])
