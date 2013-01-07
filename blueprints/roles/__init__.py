__author__ = 'HansiHE'
#Code originally by wiggitywhack with some major changes

from flask.ext.login import current_user
from flask import Blueprint, current_app, abort, request, render_template, url_for, session, redirect, flash
from flask.ext.principal import (Principal, Identity, PermissionDenied, Permission, identity_loaded,
                                 identity_changed, RoleNeed, UserNeed, AnonymousIdentity)
from flask.ext.login import current_user, user_logged_in, user_logged_out, AnonymousUser, login_required
from blueprints.auth.user_model import User
from role_model import Role_Group
from blueprints.base import mongo

roles = static_pages = Blueprint('roles', __name__,
        template_folder='templates')

Principal(current_app)

@user_logged_in.connect_via(current_app._get_current_object())
def on_user_logged_in(sender, user):
    print 'login'
    identity_changed.send(current_app, identity=Identity(user.get_id()))

@user_logged_out.connect_via(current_app._get_current_object())
def on_user_logged_out(sender, user):
    print 'logout'
    for key in ('identity.name', 'identity.auth_type'): session.pop(key, None)
    identity_changed.send(current_app, identity=AnonymousIdentity())

@identity_loaded.connect_via(current_app._get_current_object())
def on_identity_loaded(sender, identity):
    provide_roles(identity)

def provide_roles(identity):

    if identity.name == current_user.get_id():
        identity.user = current_user
    else:
        temp_user = User.objects(name=identity.name)
        if len(temp_user)==0:
            identity.user = AnonymousUser()
            return identity
        else:
            identity.user = temp_user.first()

    #TODO: potential issues, look here first
    user = identity.user
    identity.provides = set(UserNeed(identity.name))
    for role in user.roles:
        identity.provides.add(RoleNeed(role))
    for group in user.role_groups:
        for role in group.roles:
            identity.provides.add(RoleNeed(role))

    return identity



@roles.route('/roles/add_test')
@login_required
def add_test_node():
    current_user.roles.append('testnode')
    current_user.save()
    return 'y'

@roles.route('/roles/remove_test')
@login_required
def remove_test_node():
    if 'testnode' in current_user.roles:
        current_user.roles.remove('testnode')
        current_user.save()
    return 'y'

@roles.route('/roles/test_test')
@login_required
def test_test_node():
    with Permission(RoleNeed('testnode')).require(403):
        return 'yay!'