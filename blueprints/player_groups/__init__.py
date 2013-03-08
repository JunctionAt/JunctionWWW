"""
Groups
------

Endpoints for getting and editing player group data.
"""

import flask
import flask_login
from flask import render_template, jsonify, request, current_app, abort, flash, redirect, url_for
from wtforms.validators import Required, Optional, Email, ValidationError
import wtforms
from flask.ext.wtf import RecaptchaField
from flask.ext.mongoengine.wtf.orm import model_form
import re

from blueprints.auth import login_required
from blueprints.api import apidoc
from blueprints.player_groups.group_model import Group
from blueprints.notifications.notification_model import Notification

class Blueprint(flask.Blueprint):

    endpoints = dict()

    def __call__(self, servers=[]):
        for server in servers:
            self[server['name']] = Endpoint(**server)
        return self

    def __getitem__(self, key):
        return self.endpoints[key]

    def __setitem__(self, server, endpoint):
        self.endpoints[server] = endpoint

player_groups = Blueprint('player_groups', __name__, template_folder='templates')

# player_groups global
@flask.current_app.context_processor
def inject_groups():
    return dict(player_groups=player_groups)

class RecaptchaForm(wtforms.Form):
    recaptcha = RecaptchaField()

class Endpoint(object):
    """Wrapper to distinguish server groups"""

    def __init__(self, name,
                 group='group', a_group=None, groups=None,
                 member='member', a_member=None, members=None,
                 owner='owner', a_owner=None, owners=None):
        """Create a player_groups endpoint for server name"""

        self.server = name
        self.group = group
        self.a_group = a_group if a_group else "a %s"%self.group
        self.groups = groups if groups else "%ss"%self.group
        self.member = member
        self.a_member = a_member if a_member else ("a %s"%self.member if not self.member[0] in ('aeiou') else "an %s"%self.member)
        self.members = members if members else "%ss"%self.member
        self.owner = owner
        self.a_owner = a_owner if a_owner else ("a %s"%self.owner if not self.owner[0] in ('aeiou') else "an %s"%self.owner)
        self.owners = owners if owners else "%ss"%self.owner

        self.GroupEditForm = self.group_form()
        self.GroupRegisterForm = self.group_form(register=True)

        player_groups.add_url_rule(
            '/%s/%s/<group>'%(self.server, self.group), 'show_group',
            defaults=dict(server=self.server, ext='html'))
        player_groups.add_url_rule(
            '/%s/%s/invitations'%(self.server, self.groups), 'show_invitations',
            defaults=dict(server=self.server, ext='html'))
        player_groups.add_url_rule(
            '/%s/%s/register'%(self.server, self.groups), 'register_group',
            defaults=dict(server=self.server, ext='html'),
            methods=('GET', 'POST'))
        player_groups.add_url_rule(
            '/%s/%s/<group>/edit'%(self.server, self.group), 'edit_group',
            defaults=dict(server=self.server, ext='html'),
            methods=('GET','POST'))
        player_groups.add_url_rule(
            '/%s/%s/<group>/join'%(self.server, self.group), 'join_group',
            defaults=dict(server=self.server, ext='html'),
            methods=('GET', 'POST', 'DELETE'))
        player_groups.add_url_rule(
            '/%s/%s/<group>/leave'%(self.server, self.group), 'leave_group',
            defaults=dict(server=self.server, ext='html'),
            methods=('GET', 'POST'))

    def group_form(self, register=False):
        """Create a group editing form class"""

        exclude = [ 'server', 'name', 'owners', 'members', 'created' ]
        if register:
            base_class = RecaptchaForm
            description = """You will need to have at least one other confirmed %s or %s to complete registration.
                             If you do not see the player's name in the list, you must wait until the player has
                             created an account before registering your %s."""%(self.member, self.owner, self.group)
        else:
            base_class = wtforms.Form
            description = None
            exclude.append('display_name')
        return model_form(
            Group, exclude=exclude, base_class=base_class,
            field_args=dict(
                display_name=dict(
                    label='%s name'%self.group.capitalize(),
                    validators=[ Required(), self.validate_display_name ]),
                public=dict(
                    label='Open registration',
                    description='Check this to allow anyone to join your %s without prior invitation.'%self.group),
                mail=dict(
                    description='Optional. Used for avatar.',
                    validators=[ Optional(), Email() ]),
                invited_owners=dict(
                    label=self.owners.capitalize(),
                    description=description),
                invited_members=dict(
                    label=self.members.capitalize()),
            ))

    def validate_display_name(self, form, field):
        """For registration form"""

        if not re.match('[a-zA-Z0-9]', field.data):
            raise ValidationError("Your %s name must include at least letter or number."%self.group)
        display_name = re.sub(r'\s+', ' ', field.data.strip())
        gid = "%s.%s"%(self.server, re.sub(r'\s+', '_', re.sub(r'[^a-zA-Z0-9]+', '', display_name)))
        #if session.query(Group).filter(Group.id==id).count() > 0:
        #    raise ValidationError("%s name not available."%self.group.capitalize())
        if len(Group.objects(gid=gid)) > 0:
            raise ValidationError("%s name not available."%self.group.capitalize())

    def validate_members(self, form, user):
        """For registration form"""

        invited_owners = set(form.invited_owners.raw_data + [user.name])
        invited_members = list(set(form.invited_members.raw_data) - invited_owners)
        if len(invited_owners) + len(invited_members) < 2:
            form.invited_members.errors = [ "You must have at least one other %s or %s in %s."%(self.owner,self.member,self.a_group) ]
            return False
        return True

    def owner_of(self, user):
        """Returns the groups user owns"""

        return filter(lambda group: group.server == self.server, user.groups_owner)

    def member_of(self, user):
        """Returns the groups user is a member of"""

        return filter(lambda group: group.server == self.server, user.groups_member)

    def member_or_owner_of(self, user):
        """Returns the groups user is a member or owner of"""

        return filter(lambda group: group.server == self.server, user.groups_member + user.groups_owner)

    def invited_owner_of(self, user):
        """Returns the unactioned member invitations of user"""

        return filter(lambda group: group.server == self.server,\
            list(set(user.groups_invited_owner or list()) -
                 set(user.groups_owner or list())))

    def invited_member_of(self, user):
        """Returns the unactioned owner invitations of user"""

        return filter(lambda group: group.server == self.server,\
            list(set(user.groups_invited_member or list()) -
                 set(user.groups_member or list())))

    def invited_owner_or_member_of(self, user):
        """Returns the unactioned member or owner invitations of user"""

        return filter(lambda group: group.server == self.server,\
            list(set((user.groups_invited_member or list()) + (user.groups_invited_owner or list())) -
                 set((user.groups_member or list()) + ((user.groups_owner or list())))))


from .views import group_action, group_display, group_edit, group_members, group_register, group_invitations


@apidoc(__name__, player_groups, '/<server>/groups/names.json', defaults=dict(ext='json'))
def show_names_api(server, ext):
    """Returns a map of the names used by ``server`` when referring to groups, members and owners."""
    try:
        self = player_groups[server]
    except KeyError:
        abort(404)
    return jsonify(names=dict(
        group=self.group,
        a_group=self.a_group,
        groups=self.groups,
        member=self.member,
        a_member=self.a_member,
        members=self.members,
        owner=self.owner,
        a_owner=self.a_owner,
        owners=self.owners))

# Register endpoints
current_app.view_functions = dict(current_app.view_functions.items() + [
    ('player_groups.show_group', group_display.show_group),
    ('player_groups.show_members', group_members.show_members),
    ('player_groups.show_owners', group_members.show_owners),
    ('player_groups.show_invitations', group_invitations.show_invitations),
    ('player_groups.register_group', group_register.register_group),
    ('player_groups.edit_group', group_edit.edit_group),
    ('player_groups.join_group', group_action.join_group),
    ('player_groups.leave_group', group_action.leave_group),
    ('player_groups.manage_members', group_members.manage_members),
    ])

#def delete_notifications(users, group):
#    """Delete player notification"""
#
#    try:
#        session.query(Notification)\
#        .filter(Notification.user_name.in_(users))\
#        .filter(Notification.module=='player_groups')\
#        .filter(Notification.type=='invitation')\
#        .filter(Notification.from_=="%s.%s"%(group.server,group.name))\
#        .delete('fetch')
#    except TypeError:
#        return delete_notifications([users], group)
#    except:
#        abort(500)
#

def manage_notifications_p(group):
    """Save and manage invitation notifications"""

    # People who have been invited but not confirmed
    invited =\
    (set(group.invited_owners) - set(group.owners)) |\
    (set(group.invited_members) - set(group.members))
    # People who have been notified
    notified = set(map(lambda notification: notification.user,\
        session.query(Notification)\
        .filter(Notification.module=='player_groups')\
        .filter(Notification.type=='invitation')\
        .filter(Notification.from_=="%s.%s"%(group.server,group.name))\
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
                message="You have been invited to join [%s](%s)."%\
                        (group.display_name,
                         url_for('player_groups.join_group', server=group.server, group=group.name, ext='html'))))

#@notification(name='player_groups')
#def show_notifications(notifications):
#    """Display a group invitation if the profile doesn't hide them"""
#
#    # Break out the notifications by type so we can handle invitations specially
#    types = reduce(
#        lambda types, notification:
#        dict(types.items() +[(notification.type, types.get(notification.type, list()) + [notification])]),
#        notifications, dict())
#    for type_, notifications in types.iteritems():
#        if not type_ == 'invitation':
#            for notification in notifications:
#                notify('player_notifications', notification)
#        elif not flask_login.current_user.profile.hide_group_invitations:
#            # Collapse invitations by server
#            for server in player_groups.endpoints.keys():
#                if request.path == url_for('player_groups.show_invitations', server=server): continue
#                server_notifications = filter(lambda notification: notification.from_.startswith("%s."%server), notifications)
#                if len(server_notifications) > 1:
#                    notify('player_notifications', Notification(
#                        message="You have been invited to join [%d %s](%s)."%
#                                (len(server_notifications), endpoint.groups, url_for('player_groups.show_invitations',server=endpoint.name))))
#                elif len(server_notifications) == 1:
#                    if not request.path == url_for('player_groups.join_group', server=server,
#                        group=server_notifications[0].from_.split('.')[1],
#                        ext='html'):
#                        notify('player_notifications', server_notifications[0])