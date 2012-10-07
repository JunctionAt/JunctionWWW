from flask import Blueprint, current_app, abort, request
from flask.ext.principal import Principal, Identity, AnonymousIdentity, identity_changed, PermissionDenied
from flask.ext.login import current_user, login_required
from flask.ext.principal import identity_loaded, RoleNeed, UserNeed
from sqlalchemy.orm.exc import NoResultFound
from wtalchemy.orm import model_form

from blueprints.base import db
from blueprints.roles.permissions import edit_roles_permission
from blueprints.auth.user_model import User
from blueprints.player_groups import Group

principals = Principal(current_app)

class Role(db.Model):

    __tablename__ = 'roles'
    name = db.Column(db.String(16), primary_key=True)
    users = db.relation(User, secondary=lambda: UserRoleRelation.__table__, backref='roles')
    groups = db.relation(Group, secondary=lambda: GroupRoleRelation.__table__, backref='roles')

class UserRoleRelation(db.Model):

    __tablename__ = 'user_roles'
    user_name = db.Column(db.String(16), db.ForeignKey(User.name), primary_key=True)
    role_name = db.Column(db.String(16), db.ForeignKey(Role.name), primary_key=True)

class GroupRoleRelation(db.Model):

    __tablename__ = 'group_roles'
    group_id = db.Column(db.String(64), db.ForeignKey(Group.id), primary_key=True)
    role_name = db.Column(db.String(16), db.ForeignKey(Role.name), primary_key=True)


@identity_loaded.connect_via(current_app)
def on_identity_loaded(sender, identity):
    # Set the identity user object
    identity.user = current_user
    if hasattr(current_user, 'name'):
        identity.provides.add(UserNeed(current_user.name))
    if hasattr(current_user, 'roles'):
        for role in current_user.roles:
            identity.provides.add(RoleNeed(role.name))
    if hasattr(current_user, 'groups_owner'):
        for group in current_user.groups_owner:
            for role in groups.roles:
                identity.provides.add(RoleNeed(role.name))
    if hasattr(current_user, 'groups_member'):
        for group in current_user.groups_member:
            for role in groups.roles:
                identity.provides.add(RoleNeed(role.name))


roles = Blueprint(__name__, 'roles', template_folder='templates')

UserRolesForm = model_form(User, db.session, only=['roles'])
GroupRolesForm = model_form(Group, db.session, only=['roles'])

@roles.route('/profile/<player>/roles', methods=('GET','POST'))
@login_required
def edit_player_roles(player):
    try:
        with edit_roles_permission.require():
            try:
                user = db.session.query(User).filter(User.name==player).one()
                form = RolesForm(request.form, only=['roles'])
                if request.method == 'POST':
                    form.populate_obj(user)
                    db.session.add(user)
                    try:
                        db.session.commit()
                    except:
                        db.session.rollback()
                        abort(500)
                    flash('Saved')
                return render_template('edit_roles.html', obj=user)
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
        with edit_roles_permission.require():
            try:
                group = db.session.query(Group).filter(Group.name=="%s.%s"%(self.server, name)).one()
                if not group.name == name:
                    redirect(url_for('roles.edit_group_roles', server=server, group=group.name)), 301
                form = GroupRolesForm(request.form)
                if request.method == 'POST' and form.validate():
                    form.populate_obj(group)
                    db.session.add(group)
                    try:
                        db.session.commit()
                    except:
                        db.session.rollback()
                        abort(500)
                    flash('Saved')
                return render_template('edit_roles.html', obj=group)
            except NoResultFound:
                abort(404)
    except PermissionDenied:
        abort(403)
