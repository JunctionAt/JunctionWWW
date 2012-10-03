import flask
import flask_login
from flask import Blueprint, render_template, jsonify, request, current_app, abort, flash, redirect, url_for
import sqlalchemy
import sqlalchemy.orm
from sqlalchemy.orm import relation
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import *
from sqlalchemy.sql.expression import and_
from sqlalchemy import Column
from sqlalchemy.orm.exc import NoResultFound
from wtforms.validators import Required, Optional, Email, ValidationError
from wtalchemy.orm import model_form
from yell import notify
from yell.decorators import notification
import datetime
import re

from blueprints.base import Base, session
from blueprints.auth.user_model import User
from blueprints.avatar import avatar
from blueprints.player_profiles import Profile
from blueprints.player_notifications import Notification


def player_groups(servers=[]):
    """Create routes for all group endpoints defined in servers
    
    Returns the blueprint for easy setup.

    """
    
    for server in servers:
        player_groups.endpoints[server['name']] = Endpoint(**server)

    return player_groups.blueprint


class Group(Base):
    """The player group table"""

    __tablename__ = 'player_groups'
    id = Column(String(64), primary_key=True)
    server = Column(String(16))
    name = Column(String(32))
    display_name = Column(String(32))
    created = Column(DateTime(), default=datetime.datetime.utcnow)
    mail = Column(String(60))
    tagline = Column(String(256))
    link = Column(String(256))
    info = Column(Text(1024))
    public = Column(Boolean)
    owners = relation(User, secondary=lambda:GroupOwners.__table__, backref="groups_owner")
    members = relation(User, secondary=lambda:GroupMembers.__table__, backref="groups_member")
    invited_owners = relation(User, secondary=lambda:GroupInvitedOwners.__table__, backref="groups_invited_owner")
    invited_members = relation(User, secondary=lambda:GroupInvitedMembers.__table__, backref="groups_invited_member")
    
    @property
    def avatar(self):
        return avatar.avatar(self.mail)

    @staticmethod
    def confirm(pending):
        """Returns a copy of pending with a confirmed id"""
        group = Group(**reduce(
                lambda kwargs, prop: dict(kwargs.items() + [(prop, getattr(pending, prop))]),
                [ 'server',
                  'name',
                  'display_name',
                  'mail',
                  'tagline',
                  'link',
                  'info',
                  'public',
                  'owners',
                  'members',
                  'invited_owners',
                  'invited_members',
                  ], dict()))
        group.id = "%s.%s"%(group.server,group.name)
        return group

def GroupUserRelation(tablename):
    """Generate secondary table linking groups to users"""
    
    return type(tablename, (Base,), dict(
            __tablename__=tablename,
            group_id=Column(String(64), ForeignKey(Group.id), primary_key=True),
            user_name=Column(String(16), ForeignKey(User.name), primary_key=True),))

GroupOwners = GroupUserRelation('player_groups_owners')
GroupMembers = GroupUserRelation('player_groups_members')
GroupInvitedOwners = GroupUserRelation('player_groups_invited_owners')
GroupInvitedMembers = GroupUserRelation('player_groups_invited_members')


# Endpoints
player_groups.endpoints = dict()

# Blueprint
player_groups.blueprint = Blueprint('player_groups', __name__, template_folder='templates')

# player_groups global
@flask.current_app.context_processor
def inject_groups():
    return dict(player_groups=player_groups)


class Endpoint(object):
    """Wrapper to distinguish server groups"""

    def __init__(self, name,
                 group='group',
                 a_group=None,
                 groups=None,
                 member='member',
                 a_member=None,
                 members=None,
                 owner='owner',
                 a_owner=None,
                 owners=None):
        """Create a player_groups endpoint for server name"""

        self.server = name
        self.group = group
        self.a_group = a_group if a_group else "a %s"%self.group
        self.groups = groups if groups else "%ss"%self.group
        self.member = member
        self.a_member = a_member if a_member else "a %s"%self.member
        self.members = members if members else "%ss"%self.member
        self.owner = owner
        self.a_owner = a_owner if a_owner else "a %s"%self.owner
        self.owners = owners if owners else "%ss"%self.owner

        @player_groups.blueprint.route('/%s/%s/<name>'%(self.server, self.group),
                                       defaults=dict(ext='html'),
                                       endpoint='%s_show_group'%self.server)
        @player_groups.blueprint.route('/%s/%s/<name>.json'%(self.server, self.group),
                                       defaults=dict(ext='json'),
                                       endpoint='%s_show_group'%self.server)
        def show_group(name, ext):
            """Show group page, endpoint specific """

            try:
                group = session.query(Group).filter(Group.id.in_([
                            "%s.%s"%(self.server,name),
                            "%s.pending.%s"%(self.server,name)
                            ])).one()
                if not group.name == name:
                    # Redirect to preferred caps
                    return redirect(url_for('player_groups.%s_show_group'%self.server, name=group.name, ext=ext)), 301
                if ext == 'json':
                    g = dict(display_name=group.display_name)
                    if group.tagline: g['tagline']=group.tagline
                    if group.link: g['link']=group.link
                    if group.info: g['info']=group.info
                    if group.public: g['public']=group.public
                    return jsonify({group.name:g})
                return render_template('show_group.html', endpoint=self, group=group)
            except NoResultFound:
                abort(404)
        
        @player_groups.blueprint.route('/%s/%s/invitations'%(self.server, self.groups),
                                       defaults=dict(ext='html'),
                                       endpoint='%s_show_invitations'%self.server)
        @player_groups.blueprint.route('/%s/%s/invitations.json'%(self.server, self.groups),
                                       defaults=dict(ext='json'),
                                       endpoint='%s_show_invitations'%self.server)
        @flask_login.login_required
        def show_invitations(ext):
            """Show all player invitations on a server"""

            if ext == 'json':
                n=[]
                owner = self.invited_owner_of(flask_login.current_user)
                if len(owner): n += map(lambda group: dict(role=self.owner, name=group.name), owner)
                member = self.invited_member_of(flask_login.current_user)
                if len(member): n += map(lambda group: dict(role=self.member, name=group.name), member)
                return jsonify(invitations=n)
            return render_template('show_invitations.html', endpoint=self)
        
        def validate_display_name(form, field):
            """For registration form"""
            
            display_name = re.sub(r'\s+', ' ', field.data.strip())
            name = re.sub(r'\s+', '_', re.sub(r'[^a-zA-Z0-9]+', '', display_name))
            if name == '_':
                raise ValidationError("Your %s name must include at least letter or number."%self.group)
            id = "%s.%s"%(self.server, name)
            if session.query(Group).filter(Group.id==id).count() > 0:
                raise ValidationError("%s name not available."%self.group.capitalize())

        def validate_members(form, user):
            invited_owners = set(form.invited_owners.raw_data + [ user.name ])
            invited_members = list(set(form.invited_members.raw_data) - invited_owners)
            if len(invited_owners) + len(invited_members) < 2:
                form.invited_members.errors = [ "You need to invite at least one other %s or %s in order to register %s."%(self.owner,self.member,self.a_group) ]
                return False
            return True
            
        def group_form(register=False):
            """Create a group editing form class"""
            
            exclude = [ 'server', 'name', 'owners', 'members', 'created' ]
            if not register: exclude.append('display_name')
            return model_form(
                Group, session, exclude=exclude,
                field_args=dict(
                    display_name=dict(
                        label='%s name'%self.group.capitalize(),
                        validators=[ Required(), validate_display_name ]),
                    public=dict(
                        label='Open registration',
                        description='Check this to allow anyone to join your %s without prior invitation.'%self.group),
                    mail=dict(
                        description='Optional contact email for your %s. Will allow you a custom avatar.'%self.group,
                        validators=[ Optional(), Email() ]),
                    invited_owners=dict(
                        label=self.owners.capitalize()),
                    invited_members=dict(
                        label=self.members.capitalize())))

        GroupEditForm = group_form()
        GroupRegisterForm = group_form(register=True)
        
        @player_groups.blueprint.route('/%s/%s/<name>/edit'%(self.server, self.group),
                                       defaults=dict(ext='html'),
                                       endpoint='%s_edit_group'%self.server,
                                       methods=('GET',))
        @player_groups.blueprint.route('/%s/%s/<name>'%(self.server, self.group),
                                       defaults=dict(ext='html'),
                                       endpoint='%s_edit_group'%self.server,
                                       methods=('POST',))
        @player_groups.blueprint.route('/%s/%s/<name>.json'%(self.server, self.group),
                                       defaults=dict(ext='json'),
                                       endpoint='%s_edit_group'%self.server,
                                       methods=('POST',))
        @flask_login.login_required
        def edit_group(name, ext):
            """Edit group page, endpoint specific"""
            try:
                group = session.query(Group).filter(Group.id.in_([
                            "%s.%s"%(self.server,name),
                            "%s.pending.%s"%(self.server,name)
                            ])).one()
                if not group.name == name:
                    # Redirect to preferred caps
                    return redirect(url_for('player_groups.%s_edit_group'%self.server, name=group.name, ext=ext)), 301
                user = flask_login.current_user
                if not user in group.owners: abort(403)
                form = GroupEditForm(request.form, group, csrf_enabled=False)
                if request.method == 'POST' and form.validate() & validate_members(form, user):
                    form.populate_obj(group)
                    # Make ownership and membership mutually exclusive
                    group.invited_owners = list(set(group.invited_owners + [ user ]))
                    group.invited_members = list(set(group.invited_members) - set(group.invited_owners))
                    # Remove uninvited players, promote & demote
                    promotions = set(group.invited_owners) & set(group.members)
                    demotions = set(group.invited_members) & set(group.owners)
                    group.owners = list(promotions | (set(group.owners) & set(group.invited_owners)))
                    group.members = list(demotions | (set(group.members) & set(group.invited_members)))
                    # Commit
                    session.add(group)
                    session.commit()
                    # Send notifications
                    manage_notifications(group)
                    # Done
                    if ext == 'html': flash('%s saved'%self.group.capitalize())
                    return redirect(url_for('player_groups.%s_edit_group'%self.server, name=group.name, ext=ext)), 303
                if ext == 'json': return jsonify(
                    fields=reduce(lambda errors, (name, field):
                                      errors if not len(field.errors) else errors + [dict(name=name, errors=field.errors)],
                                  form._fields.iteritems(),
                                  list())), 400
                return render_template('edit_group.html', endpoint=self, form=form, group=group)
            except NoResultFound:
                abort(404)
        
        @player_groups.blueprint.route('/%s/%s/register'%(self.server, self.groups),
                                       defaults=dict(ext='html'),
                                       endpoint='%s_register_group'%self.server,
                                       methods=('GET', 'POST'))
        @player_groups.blueprint.route('/%s/%s/register.json'%(self.server, self.groups),
                                       defaults=dict(ext='json'),
                                       endpoint='%s_register_group'%self.server,
                                       methods=('POST',))
        @flask_login.login_required
        def register_group(ext):
            """Register group page, endpoint specific"""
            group = Group()
            user = flask_login.current_user
            form = GroupRegisterForm(request.form, group, csrf_enabled=False)
            if request.method == 'POST' and form.validate() & validate_members(form, user):
                form.populate_obj(group)
                # Make ownership and membership mutually exclusive
                group.invited_owners = list(set(group.invited_owners + [ user ]))
                group.invited_members = list(set(group.invited_members) - set(group.invited_owners))
                # Registree is a confirmed owner
                group.owners = [ user ]
                group.display_name = re.sub(r'\s+', ' ', group.display_name.strip())
                group.server = self.server
                group.name = re.sub(r'\s+', '_', re.sub(r'[^a-zA-Z0-9]+', '', group.display_name))
                group.id = "%s.pending.%s"%(self.server, group.name)
                # Delete any pending group registrations of the same id
                session.query(Group).filter(Group.id==id).delete()
                # Commit
                session.add(group)
                session.commit()
                # Send notifications
                manage_notifications(group)
                # Done
                if ext == 'html': flash('%s registration complete pending confirmation by other %s.'%(self.group.capitalize(), self.members))
                return redirect(url_for('player_groups.%s_show_group'%self.server, name=group.name, ext=ext)), 303
            if ext == 'json': return jsonify(
                    fields=reduce(lambda errors, (name, field):
                                      errors if not len(field.errors) else errors + [dict(name=name, errors=field.errors)],
                                  form._fields.iteritems(),
                                  list())), 400
            return render_template('edit_group.html', endpoint=self, form=form, register=True)
        
        @player_groups.blueprint.route('/%s/%s/<name>/join'%(self.server, self.group),
                                       defaults=dict(ext='html'),
                                       endpoint='%s_join_group'%self.server,
                                       methods=('GET', 'POST', 'DELETE'))
        @player_groups.blueprint.route('/%s/%s/<name>/join.json'%(self.server, self.group),
                                       defaults=dict(ext='json'),
                                       endpoint='%s_join_group'%self.server,
                                       methods=('POST','DELETE'))
        @flask_login.login_required
        def join_group(name, ext):
            """Join group page, endpoint specific"""
            
            try:
                group = session.query(Group).filter(Group.id.in_([
                            "%s.%s"%(self.server,name),
                            "%s.pending.%s"%(self.server,name)
                            ])).one()
                user = flask_login.current_user
                if not group.name == name:
                    # Redirect to preferred caps
                    return redirect(url_for('player_groups.%s_join_group'%self.server, name=group.name, ext=ext)), 301
                if not user in group.members and not user in group.owners:
                    if request.method in ('POST', 'DELETE'):
                        if request.method == 'POST':
                            # Join action
                            if not group.public and user in group.invited_owners:
                                group.owners.append(user)
                            elif group.public or user in group.invited_members:
                                group.members.append(user)
                                # Maintain invited status for members of public groups
                                group.invited_members = list(set(group.invited_members + [ user ]))
                            else:
                                abort(403)
                            # Check for confirmation of group registration
                            if group.id == "%s.pending.%s"%(self.server,group.name):
                                session.delete(group)
                                group = Group.confirm(group)
                            if ext == 'html': flash("You have joined %s."%group.display_name)
                        else:
                            # Pass action
                            if user in group.invited_owners:
                                group.invited_owners -= [user]
                            elif user in group.invited_members:
                                group.invited_members -= [user]
                            else:
                                abort(403)
                            if ext == 'html': flash("Invitation to %s declined."%group.display_name)
                        manage_notifications(group)
                        session.add(group)
                        session.commit()
                        return redirect(url_for('player_groups.%s_show_group'%self.server, name=group.name, ext=ext)), 303
                    return render_template('join_group.html', endpoint=self, group=group)
                abort(403)
            except NoResultFound:
                abort(404)
        
        @player_groups.blueprint.route('/%s/%s/<name>/leave'%(self.server, self.group),
                                       defaults=dict(ext='html'),
                                       endpoint='%s_leave_group'%self.server,
                                       methods=('GET', 'POST'))
        @player_groups.blueprint.route('/%s/%s/<name>/leave.json'%(self.server, self.group),
                                       defaults=dict(ext='json'),
                                       endpoint='%s_leave_group'%self.server,
                                       methods=('POST',))
        @flask_login.login_required
        def leave_group(name, ext):
            """Leave group page, endpoint specific"""
            
            try:
                group = session.query(Group).filter(Group.id.in_([
                            "%s.%s"%(self.server,name),
                            "%s.pending.%s"%(self.server,name)
                            ])).one()
                user = flask_login.current_user
                if not group.name == name:
                    # Redirect to preferred caps
                    return redirect(url_for('player_groups.%s_leave_group'%self.server, name=group.name, ext=ext)), 301
                if user in group.members or user in group.owners:
                    if request.method == 'POST':
                        group.owners -= [user]
                        group.members -= [user]
                        group.invited_owners -= [user]
                        group.invited_members -= [user]
                        session.add(group)
                        session.commit()
                        if ext == 'html': flash("You are no longer %s of %s."%(group.a_member, group.display_name))
                        return redirect(url_for('player_groups.%s_show_group'%self.server, name=group.name, ext=ext)), 303
                    return render_template('leave_group.html', endpoint=self, group=group)
                abort(403)
            except NoResultFound:
                abort(404)
        
        @player_groups.blueprint.route('/%s/%s/<name>/%s/<player>'%(self.server, self.group, self.members),
                                       defaults=dict(ext='html'),
                                       endpoint='%s_manage_members'%self.server,
                                       methods=('GET', 'PUT','DELETE'))
        @player_groups.blueprint.route('/%s/%s/<name>/%s/<player>.json'%(self.server, self.group, self.members),
                                       defaults=dict(ext='json'),
                                       endpoint='%s_manage_members'%self.server,
                                       methods=('GET', 'PUT','DELETE'))
        @flask_login.login_required
        def manage_members(name, player, ext):
            """Group member query and management"""

            try:
                group = session.query(Group).filter(Group.id.in_([
                            "%s.%s"%(self.server,name),
                            "%s.pending.%s"%(self.server,name)
                            ])).one()
                member = session.query(User).filter(User.name==player)
                if not group.name == name or not member.name == player:
                    # Redirect to preferred caps
                    return redirect(url_for('player_groups.%s_manage_members'%self.server, name=group.name, player=member.name, ext=ext)), 301
                if request.method == 'GET':
                    # Test for membership
                    if member in group.members:
                        return redirect(url_for('player_profiles.show_profile', name=member.name, ext=ext)), 303
                    abort(404)
                elif user in group.owners:
                    if request.method == 'PUT' and not user == member and not member in group.invited_members:
                        # Add membership
                        if member in group.owners:
                            # demotion
                            group.owners -= [member]
                            group.members += [member] 
                        group.invited_owners -= [member]
                        group.invited_members += [member]
                        manage_notifications(group)
                        session.add(group)
                        session.commit()
                        return redirect(url_for('player_groups.%s_manage_members'%self.server, name=group.name, player=member.name, ext=ext)), 303
                    elif request.method == 'DELETE':
                        if member in groups.invited_members or member in groups.members:
                            # Remove membership
                            group.members -= [member]
                            group.invited_members -= [member]
                            manage_notifications(group)
                            session.add(group)
                            session.commit()
                            return redirect(url_for('player_groups.%s_manage_members'%self.server, name=group.name, player=member.name, ext=ext)), 303
                        abort(404)
                abort(403)
            except NoResultFound:
                abort(404)
        
        @player_groups.blueprint.route('/%s/%s/<name>/%s/<player>'%(self.server, self.group, self.owners),
                                       defaults=dict(ext='html'),
                                       endpoint='%s_manage_owners'%self.server,
                                       methods=('GET', 'PUT','DELETE'))
        @player_groups.blueprint.route('/%s/%s/<name>/%s/<player>.json'%(self.server, self.group, self.owners),
                                       defaults=dict(ext='json'),
                                       endpoint='%s_manage_owners'%self.server,
                                       methods=('GET', 'PUT','DELETE'))
        @flask_login.login_required
        def manage_owners(name, player, ext):
            """Group owner query and management"""

            try:
                group = session.query(Group).filter(Group.id.in_([
                            "%s.%s"%(self.server,name),
                            "%s.pending.%s"%(self.server,name)
                            ])).one()
                owner = session.query(User).filter(User.name==player)
                if not group.name == name or not owner.name == player:
                    # Redirect to preferred caps
                    return redirect(url_for('player_groups.%s_manage_owners'%self.server, name=group.name, player=owner.name, ext=ext)), 301
                if request.method == 'GET':
                    # Test for ownership
                    if member in group.owners:
                        return redirect(url_for('player_profiles.show_profile', name=member.name, ext=ext)), 303
                    abort(404)
                elif user in group.owners:
                    if request.method == 'PUT' and not user == owner and not owner in group.invited_owners:
                        # Add ownership
                        if owner in group.members:
                            # Promotion
                            group.members -= [owner]
                            group.owners += [owner]
                        group.invited_members -= [owner]
                        group.invited_owners += [owner]
                        manage_notifications(group)
                        session.add(group)
                        session.commit()
                        return redirect(url_for('player_groups.%s_manage_owners'%self.server, name=group.name, player=owner.name, ext=ext)), 303
                    elif request.method == 'DELETE':
                        if owner in groups.invited_owners or owner in groups.owners:
                            # Remove ownership
                            group.owner -= [owner]
                            group.invited_owner -= [owner]
                            manage_notifications(group)
                            session.add(group)
                            session.commit()
                            return redirect(url_for('player_groups.%s_manage_owners'%self.server, name=group.name, player=owner.name, ext=ext)), 303
                        abort(404)
                abort(403)
            except NoResultFound:
                abort(404)
        
        def delete_notifications(users, group):
            """Delete player notification"""
            
            try:
                iter(users)
            except TypeError:
                return delete_notifications([users], group)
            session.query(Notification) \
                .filter(Notification.module=='player_groups') \
                .filter(Notification.type=='invitation') \
                .filter(Notification.from_=="%s.%s"%(group.server,group.name)) \
                .filter(Notification.user_name.in_(users)) \
                .delete()

        def manage_notifications(group):
            """Save and manage invitation notifications"""

            # People who have been invited but not confirmed
            invited = \
                (set(group.invited_owners) - set(group.owners)) | \
                (set(group.invited_members) - set(group.members))
            # People who have been notified
            notified = set(map(lambda notification: notification.user, \
                                   session.query(Notification) \
                                   .filter(Notification.module=='player_groups') \
                                   .filter(Notification.type=='invitation') \
                                   .filter(Notification.from_=="%s.%s"%(group.server,group.name)) \
                                   .all()))
            # Delete notifications for players that are no longer invited
            delete_notifications(map(lambda user: user.name, notified - invited), group)
            # Add notifications for people who haven't been sent one
            for user in invited - notified:
                session.add(
                    Notification(
                        user_name=user.name,
                        module='player_groups',
                        type='invitation',
                        from_="%s.%s"%(group.server,group.name),
                        message="You have been invited to join [%s](%s)."% \
                            (group.display_name,
                             url_for('player_groups.%s_join_group'%group.server, name=group.name))))
            session.commit()

    def owner_of(self, user):
        """Returns the groups user owns"""
        
        return filter(lambda group: group.server == self.server, user.groups_owner)

    def member_of(self, user):
        """Returns the groups user is a member of"""
        
        return filter(lambda group: group.server == self.server, user.groups_member)

    def invited_owner_of(self, user):
        """Returns the unactioned member invitations of user"""
        
        return filter(lambda group: group.server == self.server, \
                          list(set(flask_login.current_user.groups_invited_owner or list()) -
                               set(flask_login.current_user.groups_owner or list())))

    def invited_member_of(self, user):
        """Returns the unactioned owner invitations of user"""
        
        return filter(lambda group: group.server == self.server, \
                          list(set(flask_login.current_user.groups_invited_member or list()) -
                               set(flask_login.current_user.groups_member or list())))

@notification(name='player_groups')
def show_notifications(notifications):
    """Display a group invitation if the profile doesn't hide them"""
    
    # Break out the notifications by type so we can handle invitations specially
    types = reduce(
        lambda types, notification:
            dict(types.items() +[(notification.type, types.get(notification.type, list()) + [notification])]),
        notifications, dict())
    for type_, notifications in types.iteritems():
        if not type_ == 'invitation':
            for notification in notifications:
                notify('player_notifications', notification)
        elif not flask_login.current_user.profile.hide_group_invitations:
            # Collapse invitations by server
            for server in player_groups.endpoints.keys():
                if request.path == url_for('player_groups.%s_show_invitations'%server): continue
                server_notifications = filter(lambda notification: notification.from_.startswith("%s."%server), notifications)
                if len(server_notifications) > 1:
                    notify('player_notifications', Notification(
                            message="You have been invited to join [%d %s](%s)."%
                            (len(server_notifications), endpoint.groups, url_for('player_groups.%s_show_invitations'%endpoint.name))))
                elif len(server_notifications) == 1:
                    if not request.path == url_for('player_groups.%s_join_group'%server,
                                                   name=server_notifications[0].from_.split('.')[1]):
                        notify('player_notifications', server_notifications[0])

