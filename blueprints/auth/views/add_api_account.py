__author__ = 'HansiHE'

from flask import render_template
from blueprints.auth import login_required, current_user
from blueprints.auth.util import require_permissions
from .. import blueprint


@blueprint.route('/auth/add_api_account', methods=['GET', 'POST'])
@require_permissions('admin.add_api_account')
def add_api_account():
    return render_template('add_api_account.html')