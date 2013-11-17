__author__ = 'HansiHE'

from flask import render_template
from .. import blueprint
from blueprints.auth.user_model import User, Role_Group

@blueprint.route('/staff/')
def view_staff():
    mods = User.objects(role_groups__in=[Role_Group.objects(name="moderator").order_by('name').first()])
    techs = User.objects(role_groups__in=[Role_Group.objects(name="technical").order_by('name').first()])

    return render_template('staff_view_staff.html', mods=mods, techs=techs, title="Staff")
