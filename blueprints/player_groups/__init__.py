import flask
import flask_login
from flask import Blueprint, render_template, request, current_app, abort, flash, redirect, url_for
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
    mail = Column(String(256))
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
                 groups='groups',
                 member='member',
                 members='members',
                 owner='owner',
                 owners='owners'):
        """Create a player_groups endpoint for server name"""

        self.server = name
        self.group = group
        self.groups = groups
        self.member = member
        self.members = members
        self.owner = owner
        self.owners = owners

        @player_groups.blueprint.route('/%s/%s/<name>'%(self.server, self.group),
                                       endpoint='%s_show_group'%self.server)
        def show_group(name):
            """Show group page, endpoint specific """

            try: group = session.query(Group).filter(Group.id.in_([
                        "%s.%s"%(self.server,name),
                        "%s.pending.%s"%(self.server,name)
                        ])).first()
            except NoResultFound: abort(404)
            if not group.name == name:
                # Redirect to preferred caps
                return redirect(url_for('player_groups.%s_show_group'%self.server, name=group.name))
            return render_template('show_group.html', endpoint=self, group=group)
        
        @player_groups.blueprint.route('/%s/%s/invitations'%(self.server, self.groups),
                                       endpoint='%s_show_invitations'%self.server)
        @flask_login.login_required
        def show_invitations():
            """Show all player invitations on a server"""
            
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
                        validators=[Optional(), Email()]),
                    invited_owners=dict(
                        label=self.owners.capitalize()),
                    invited_members=dict(
                        label=self.members.capitalize())))

        GroupEditForm = group_form()
        GroupRegisterForm = group_form(register=True)
        
        @player_groups.blueprint.route('/%s/%s/<name>/edit'%(self.server, self.group),
                                       endpoint='%s_edit_group'%self.server,
                                       methods=('GET', 'POST'))
        @flask_login.login_required
        def edit_group(name):
            """Edit group page, endpoint specific"""
            try: group = session.query(Group).filter(Group.id.in_([
                        "%s.%s"%(self.server,name),
                        "%s.pending.%s"%(self.server,name)
                        ])).first()
            except NoResultFound: abort(404)
            user = User.current_user
            if not user in group.owners: abort(403)
            form = GroupEditForm(request.form, group)
            if request.method == 'POST' and form.validate():
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
                manage_invitations(group)
                # Done
                flash('%s saved'%self.group.capitalize())
                return redirect(url_for('player_groups.%s_edit_group'%self.server, name=group.name))
            if not group.name == name:
                # Redirect to preferred caps
                return redirect(url_for('player_groups.%s_edit_group'%self.server, name=group.name))
            return render_template('edit_group.html', endpoint=self, form=form, group=group)
        
        @player_groups.blueprint.route('/%s/%s/register'%(self.server, self.groups),
                                       endpoint='%s_register_group'%self.server,
                                       methods=('GET', 'POST'))
        @flask_login.login_required
        def register_group():
            """Register group page, endpoint specific"""
            group = Group()
            form = GroupRegisterForm(request.form, group, register=True)
            user = User.current_user
            if request.method == 'POST' and form.validate():
                form.populate_obj(group)
                group.display_name = re.sub(r'\s+', ' ', group.display_name.strip())
                group.server = self.server
                group.name = re.sub(r'\s+', '_', re.sub(r'[^a-zA-Z0-9]+', '', group.display_name))
                group.id = "%s.pending.%s"%(self.server, group.name)
                # Make ownership and membership mutually exclusive
                group.invited_owners = list(set(group.invited_owners + [ user ]))
                group.invited_members = list(set(group.invited_members) - set(group.invited_owners))
                # Registree is a confirmed owner
                group.owners = [ user ]
                # Delete any pending group registrations of the same id
                session.query(Group).filter(Group.id==id).delete()
                # Commit
                session.add(group)
                session.commit()
                # Send notifications
                manage_invitations(group)
                # Done
                flash('%s registration complete pending confirmation by other %s.'%(self.group.capitalize(), self.members))
                return redirect(url_for('player_groups.%s_show_group'%self.server, name=group.name))
            return render_template('edit_group.html', endpoint=self, form=form, register=True)
        
        @player_groups.blueprint.route('/%s/%s/<name>/join'%(self.server, self.group),
                                       endpoint='%s_join_group'%self.server,
                                       methods=('GET', 'POST'))
        @flask_login.login_required
        def join_group(name):
            """Join group page, endpoint specific"""
            try: group = session.query(Group).filter(Group.id.in_([
                        "%s.%s"%(self.server,name),
                        "%s.pending.%s"%(self.server,name)
                        ])).first()
            except NoResultFound: abort(404)
            user = User.current_user
            if not user in group.members and not user in group.owners:
                if request.method == 'POST':
                    if request.form['action'] == 'accept':
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
                        flash("You have joined %s."%group.display_name)
                    else:
                        # Pass action
                        if user in group.invited_owners:
                            group.invited_owners.remove(user)
                        elif user in group.invited_members:
                            group.invited_members.remove(user)
                        else:
                            abort(403)
                        flash("Invitation to %s declined."%group.display_name)
                    # Delete player notification
                    session.query(Notification) \
                        .filter(Notification.module=='player_groups') \
                        .filter(Notification.type=='invitation') \
                        .filter(Notification.from_=="%s.%s"%(group.server,group.name)) \
                        .filter(Notification.user_name==user.name) \
                        .delete()
                    session.add(group)
                    session.commit()
                    return redirect(url_for('player_groups.%s_show_group'%self.server, name=group.name))
                if not group.name == name:
                    # Redirect to preferred caps
                    return redirect(url_for('player_groups.%s_join_group'%self.server, name=group.name))
                return render_template('join_group.html', endpoint=self, group=group)
            abort(403)

        def manage_invitations(group):
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
            session.query(Notification) \
                .filter(Notification.module=='player_groups') \
                .filter(Notification.type=='invitation') \
                .filter(Notification.from_=="%s.%s"%(group.server,group.name)) \
                .filter(Notification.user_name.in_(map(lambda user: user.name, notified - invited))) \
                .delete()
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

    def owned_by(self, user):
        """Returns the groups user owns"""
        
        return filter(lambda group: group.server == self.server, user.groups_owner)

    def member_of(self, user):
        """Returns the groups user is a member of"""
        
        return filter(lambda group: group.server == self.server, user.groups_member)

    def invited_owner_of(self, user):
        """Returns the unactioned member invitations of user"""
        
        return filter(lambda group: group.server == self.server, \
                          list(set(User.current_user.groups_invited_owner or list()) -
                               set(User.current_user.groups_owner or list())))

    def invited_member_of(self, user):
        """Returns the unactioned owner invitations of user"""
        
        return filter(lambda group: group.server == self.server, \
                          list(set(User.current_user.groups_invited_member or list()) -
                               set(User.current_user.groups_member or list())))


@player_groups.blueprint.route('/groups/<server>/show/<name>')
def show_group(server, name):
    """Redirects to preferred url of server"""
    endpoint = player_groups.endpoints.get(server)
    if endpoint:
        return redirect(url_for('player_groups.%s_show_group'%endpoint.server, name=name))
    abort(404)

@player_groups.blueprint.route('/groups/<server>/edit/<name>')
def edit_group(server, name):
    """Redirects to preferred url of server"""
    endpoint = player_groups.endpoints.get(server)
    if endpoint:
        return redirect(url_for('player_groups.%s_edit_group'%endpoint.server, name=name))
    abort(404)

@player_groups.blueprint.route('/groups/<server>/register')
def register_group(server):
    """Redirects to preferred url of server"""
    endpoint = player_groups.endpoints.get(server)
    if endpoint:
        return redirect(url_for('player_groups.%s_register_group'%endpoint.server))
    abort(404)

@player_groups.blueprint.route('/groups/<server>/invitations')
def register_group(server):
    """Redirects to preferred url of server"""
    endpoint = player_groups.endpoints.get(server)
    if endpoint:
        return redirect(url_for('player_groups.%s_show_invitations'%endpoint.server))
    abort(404)


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
        elif not User.current_user.profile.hide_group_invitations:
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

