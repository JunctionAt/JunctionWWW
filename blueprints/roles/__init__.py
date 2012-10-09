from flask import Blueprint, current_app, abort, request, render_template, url_for, session, redirect
from flask.ext.principal import (Principal, Identity, PermissionDenied, Permission,
                                 identity_loaded, identity_changed, RoleNeed, UserNeed, AnonymousIdentity)
from flask.ext.login import current_user, user_logged_in, user_logged_out, AnonymousUser
from sqlalchemy.orm.exc import NoResultFound
from wtalchemy.orm import model_form
import re

from blueprints.auth import login_required
from blueprints.base import db
from blueprints.auth.user_model import User
from blueprints.player_groups import Group, player_groups

principals = Principal(current_app)

class Role(db.Model):

    __tablename__ = 'roles'
    name = db.Column(db.String(16), primary_key=True)
    display_name = db.Column(db.String(100))
    users = db.relation(User, secondary=lambda: UserRoleRelation.__table__, backref='roles')
    groups = db.relation(Group, secondary=lambda: GroupRoleRelation.__table__, backref='roles')

    def __repr__(self):
        return self.display_name or self.name

class UserRoleRelation(db.Model):

    __tablename__ = 'users_roles'
    user_name = db.Column(db.String(16), db.ForeignKey(User.name), primary_key=True)
    role_name = db.Column(db.String(16), db.ForeignKey(Role.name), primary_key=True)

class GroupRoleRelation(db.Model):

    __tablename__ = 'player_groups_roles'
    group_id = db.Column(db.String(64), db.ForeignKey(Group.id), primary_key=True)
    role_name = db.Column(db.String(16), db.ForeignKey(Role.name), primary_key=True)


@user_logged_in.connect_via(current_app._get_current_object())
def on_user_logged_in(sender, user):
    identity_changed.send(current_app, identity=Identity(user.name))

@user_logged_out.connect_via(current_app._get_current_object())
def on_user_logged_out(sender, user):
    for key in ('identity.name', 'identity.auth_type'): session.pop(key, None)
    identity_changed.send(current_app, identity=AnonymousIdentity())

@identity_loaded.connect_via(current_app._get_current_object())
def on_identity_loaded(sender, identity):
    identity_roles(identity)

def identity_roles(identity):
    identity.provides = set(UserNeed(identity.name))
    if current_user.is_authenticated() and identity.name == current_user.name:
        identity.user = current_user
    else:
        try:
            identity.user = db.session.query(User).filter(User.name==identity.name).one()
        except NoResultFound:
            identity.user = AnonymousUser()
    if hasattr(identity.user, 'roles'):
        for role in identity.user.roles:
            identity.provides.add(RoleNeed(role.name))
    if hasattr(identity.user, 'groups_owner'):
        for group in identity.user.groups_owner:
            for role in group.roles:
                identity.provides.add(RoleNeed(role.name))
    if hasattr(identity.user, 'groups_member'):
        for group in identity.user.groups_member:
            for role in group.roles:
                identity.provides.add(RoleNeed(role.name))
    return identity

roles = Blueprint('roles', __name__, template_folder='templates')

UserRolesForm = model_form(User, db.session, only=['roles'])
GroupRolesForm = model_form(Group, db.session, only=['roles'])

@roles.route('/profile/<player>/roles', methods=('GET','POST'))
@login_required
def edit_player_roles(player):
    try:
        with Permission(RoleNeed('edit_roles')).require(): pass
        user = db.session.query(User).filter(User.name==player).one()
        if not user.name == player:
            redirect(url_for('roles.edit_player_roles', player=user.name)), 301
        form = UserRolesForm(request.form, user, only=['roles'])
        if request.method == 'POST':
            form.populate_obj(user)
            db.session.add(user)
            try:
                db.session.commit()
            except:
                db.session.rollback()
                abort(500)
            flash('Saved')
        return render_template('edit_roles.html', form=form, name=user.name, action=url_for('roles.edit_player_roles', player=user.name))
    except NoResultFound:
        abort(404)
    except PermissionDenied:
        abort(403)

@roles.route('/<server>/group/<group>/roles', methods=('GET','POST'))
@login_required
def edit_group_roles(server, group):
    name = group
    try:
        self = player_groups[server]
    except KeyError:
        abort(404)
    try:
        with Permission(RoleNeed('edit_roles')).require(403): pass
        group = db.session.query(Group).filter(Group.id=="%s.%s"%(self.server, name)).one()
        if not group.name == name:
            redirect(url_for('roles.edit_group_roles', server=server, group=group.name)), 301
        form = GroupRolesForm(request.form, group)
        if request.method == 'POST' and form.validate():
            form.populate_obj(group)
            db.session.add(group)
            try:
                db.session.commit()
            except:
                db.session.rollback()
                abort(500)
            flash('Saved')
        return render_template('edit_roles.html', form=form, name=group.name, action=url_for('roles.edit_group_roles', server=server, group=group.name))
    except NoResultFound:
        abort(404)
