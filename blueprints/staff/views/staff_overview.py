__author__ = 'HansiHE'

from flask import render_template
from .. import blueprint
from blueprints.auth.user_model import User, Role_Group

@blueprint.route('/staff/')
def view_staff():
    staff = User.objects(role_groups__in=[Role_Group.objects(name="moderator").first()])

    return render_template('staff_view_staff.html', staff=staff, title="Staff")
