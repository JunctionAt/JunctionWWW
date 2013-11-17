__author__ = 'HansiHE'

from flask import render_template
from .. import blueprint
from blueprints.auth.user_model import User, Role_Group
from random import shuffle

@blueprint.route('/staff/')
def view_staff():
    mods = User.objects(role_groups__in=[Role_Group.objects(name="moderator").first()])
    mods = list(mods)
    shuffle(mods)
    techs = User.objects(role_groups__in=[Role_Group.objects(name="technical").first()])
    techs = list(techs)
    shuffle(techs)
    inactives = User.objects(role_groups__in=[Role_Group.objects(name="inactive").first()])
    inactives = list(inactives)
    shuffle(inactives)

    return render_template('staff_view_staff.html', mods=mods, techs=techs, inactives=inactives, title="Staff")
