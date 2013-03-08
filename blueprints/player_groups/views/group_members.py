__author__ = 'HansiHE'

import flask_login
from flask import render_template, jsonify, request, current_app, abort, flash, redirect, url_for
from mongoengine import *

from blueprints.auth.user_model import User
from blueprints.api import apidoc

from blueprints.player_groups.group_model import Group

from blueprints.player_groups import player_groups

@apidoc(__name__, player_groups, '/<server>/group/<group>/members.json', endpoint='show_members', defaults=dict(ext='json'))
def show_members_api(server, group, ext):
    """List players that are currently invited and have accepted membership of ``group``.

    Returns an object with its primary key being the preferred name for members of ``server``'s groups. Eg.:

    .. code-block::

       {
           "citizens": [
               "wiggitywhack",
               "sparkle_bombs",
               "jmanthethief"
           ]
       }
    """

def show_members(server, group, ext):
    try:
        self = player_groups[server]
    except KeyError:
        abort(404)
    name = group
    #group = session.query(Group).filter(Group.id.in_([
    #    "%s.%s"%(self.server,name),
    #    "%s.pending.%s"%(self.server,name)
    #])).one()
    group = Group.objects(gid__in=[
        "%s.%s"%(self.server,name),
        "%s.pending.%s"%(self.server,name)
    ]).first()
    if group is None:
        abort(404)
    if not group.name == name:
        # Redirect to preferred caps
        return redirect(url_for('player_groups.show_members', server=server, group=group.name, ext=ext)), 301
    if ext == 'json':
        return jsonify({self.members:map(lambda member: member.name, group.members)})
        #return render_template('show_members.html', endpoint=self, group=group)
    abort(404)


@apidoc(__name__, player_groups, '/<server>/group/<group>/owners.json', endpoint='show_owners', defaults=dict(ext='json'))
def show_owners_api(server, group, ext):
    """List players that are currently invited and have accepted ownership of ``group``.

    Returns an object with its primary key being the preferred name for owners of ``server``'s groups. Eg.:

    .. code-block::

       {
           "mayors": [
               "Notch",
               "jeb_",
               "dinnerbone"
           ]
       }
    """

def show_owners(server, group, ext):
    try:
        self = player_groups[server]
    except KeyError:
        abort(404)
    name = group
    #group = session.query(Group).filter(Group.id.in_([
    #    "%s.%s"%(self.server,name),
    #    "%s.pending.%s"%(self.server,name)
    #])).one()
    group = Group.objects(gid__in=[
        "%s.%s"%(self.server,name),
        "%s.pending.%s"%(self.server,name)
    ]).first()
    if group is None:
        abort(404)
    if not group.name == name:
        # Redirect to preferred caps
        return redirect(url_for('player_groups.show_owners', server=server, group=group.name, ext=ext)), 301
    if ext == 'json':
        return jsonify({self.owners:map(lambda owner: owner.name, group.owners)})
        #return render_template('show_members.html', endpoint=self, group=group)
    abort(404)


@apidoc(__name__, player_groups, '/<server>/groups/membership/<player>.json', defaults=dict(ext='json'))
def membership(server, player, ext):
    """ Get all groups ``player`` is a member of. """
    try:
        self = player_groups[server]
    except KeyError:
        abort(404)
    user = User.objects(name=player).first()
    if user is None:
        abort(404)
    if not user.name == player:
        # Redirect to preferred caps
        return redirect(url_for('player_groups.membership', server=server, player=user.name, ext=ext)), 301
    groupsR = Group.objects(owners__in=user.name)
    return jsonify(groups=reduce(lambda groups, group: groups + [group.name], groupsR, []))


@apidoc(__name__, player_groups, '/<server>/groups/ownership/<player>.json', defaults=dict(ext='json'))
def ownership(server, player, ext):
    """ Get all groups ``player`` is an owner of. """
    try:
        self = player_groups[server]
    except KeyError:
        abort(404)
    user = User.objects(name=player).first()
    if user is None:
        abort(404)
    if not user.name == player:
        # Redirect to preferred caps
        return redirect(url_for('player_groups.membership', server=server, player=user.name, ext=ext)), 301
    groupsR = Group.objects(owners__in=user.name)
    return jsonify(groups=reduce(lambda groups, group: groups + [group.name], groupsR, []))


@apidoc(__name__, player_groups, '/<server>/group/<group>/<any(all,member,owner):type>/<player>.json', endpoint='manage_members', defaults=dict(ext='json', invite=None), methods=('GET',))
def manage_members_get_api(server, group, invite, type, player, ext):
    """
    Used to assert ``player``'s membership in ``group`` as specified by ``type``. These endpoints are only valid after ``player`` has accepted an invitation to join ``group``. Eg.

    ``/server/group/foo/all/bar.json``
        Succeeds if player ``bar`` is a member *or* owner of group ``bar``.
    ``/server/group/foo/member/baz.json``
        Succeeds if player ``baz`` is a member of group ``foo`` and *not* an owner.
    ``/server/group/foo/owner/qux.json``
        Succeeds if player ``qux`` is an owner of group ``foo`` and *not* an member.
    """

@apidoc(__name__, player_groups, '/<server>/group/<group>/<any(member,owner):type>/<player>.json', endpoint='manage_members', defaults=dict(ext='json', invite=None), methods=('PUT',))
def manage_members_put_api(server, group, invite, type, player, ext):
    """
    Used by an owner of ``group`` to promote or demote ``player``'s membership status as specified by ``type``.

    This resource is only valid if ``player`` is currently a member or owner of group, which requires ``player`` accepting an invitation to join ``group``.

    If ``player`` is currently an owner of ``group`` and ``type`` is ``"member"``, this will demote ``player`` without
    sending an invitation for ``player`` to accept the new role.

    If ``player`` is currently a member of ``group`` and ``type`` is ``"owner"``, this will promote ``player`` without
    sending an invitation for ``player`` to accept the new role.
    """

@apidoc(__name__, player_groups, '/<server>/group/<group>/invited/all/<player>.json', endpoint='manage_members', defaults=dict(ext='json', type='all', invite=True), methods=('DELETE',))
def manage_invited_members_delete_api(server, group, invite, type, ext):
    """
    Used by an owner of ``group`` to remove  ``player``'s invitation *and* membership.

    This resource remains valid after ``player`` has accepted an invitation to ``group`` and is the only way to revoke a player's membership or invitation to join.
    """

@apidoc(__name__, player_groups, '/<server>/group/<group>/invited/<any(all,member,owner):type>/<player>.json', endpoint='manage_members', defaults=dict(ext='json', invite=True), methods=('GET',))
def manage_invited_members_get_api(server, group, invite, type, player, ext):
    """
    Used to assert ``player``'s invitation status in ``group`` as specified by ``type``.

    This resource may be valid after ``player`` has accepted an invitation to join ``group`` with regards to ``player``'s membership status being ``type``.
    """

@apidoc(__name__, player_groups, '/<server>/group/<group>/invited/<any(member,owner):type>/<player>.json', endpoint='manage_members', defaults=dict(ext='json', invite=True), methods=('PUT',))
def manage_invited_members_put_api(server, group, invite, type, player, ext):
    """
    Used by an owner of ``group`` to invite ``player`` to the membership status as specified by ``type``.

    This resource is no longer valid after ``player`` has accepted an invitation to join ``group``.
    """

def manage_members(server, group, invite, type, player, ext):
    """World's largest function"""

    try:
        self = player_groups[server]
    except KeyError:
        abort(404)
    def members(group, val=None, invite=invite):
        f = 'invited_members' if invite else 'members'
        if val == None:
            return getattr(group, f)
        setattr(group, f, val)
    def owners(group, val=None, invite=invite):
        f = 'invited_owners' if invite else 'owners'
        if val == None:
            return getattr(group, f)
        setattr(group, f, val)
    def to(group, val=None, t=type, invite=invite):
        return dict(
            all=lambda: members(group, invite=invite) + owners(group, invite=invite),
            member=lambda: members(group, val, invite),
            owner=lambda: owners(group, val, invite)
        )[t]()
    def from_(group, val=None, t=type, invite=invite):
        return dict(
            member=lambda: owners(group, val, invite),
            owner=lambda: members(group, val, invite)
        )[t]()
    name = group
    group = Group.objects(gid__in=[
        "%s.%s"%(self.server,name),
        "%s.pending.%s"%(self.server,name)
    ]).first()
    if group is None:
        abort(404)
    member = User.objects(name=player).first()
    if member is None:
        abort(404)
    user = flask_login.current_user
    if not group.name == name or not member.name == player:
        # Redirect to preferred caps
        return redirect(url_for('player_groups.manage_members', server=server, group=group.name, type=type, player=member.name, ext=ext)), 301
    if request.method == 'GET' and not invite:
        # Test for membership
        if member in to(group):
            return redirect(url_for('player_profiles.show_profile', player=member.name, ext=ext)), 302
        abort(404)
    if user.is_authenticated() and user in group.owners:
        if request.method == 'GET': # invite == True
            # Test for membership
            if member in to(group) or member in to(group, invite=None):
                return redirect(url_for('player_profiles.show_profile', player=member.name, ext=ext)), 302
            abort(404)
        elif request.method == 'PUT' and (invite or member in from_(group)):
            if invite and (member in group.owners or member in group.members):
                # This is no longer a valid resource once the member has joined
                abort(403)
            from_(group, list(set(from_(group)) - set([member])))
            to(group, list(set(to(group) + [member])))
            if invite:
                #manage_notifications(group) #TODO: Notifications!!
                pass
            else:
                # mirror invited status with membership status
                from_(group, list(set(from_(group, invite=True)) - set([member])), invite=True)
                to(group, list(set(to(group, invite=True) + [member])), invite=True)
                # Commit
            group.save()
            return redirect(url_for('player_groups.manage_members', server=server, group=group.name, type=type, invite=invite, player=member.name, ext=ext)), 303
        elif request.method == 'DELETE' and member in to(group):
            # Remove membership and ownership
            group.members = list(set(group.members) - set([member]))
            group.owners = list(set(group.owners) - set([member]))
            group.invited_members = list(set(group.invited_members) - set([member]))
            group.invited_owners = list(set(group.invited_owners) - set([member]))
            group.member_count -= 1
            #manage_notifications(group) #TODO: Notifications!!
            # Commit
            group.save()
            return redirect(url_for('player_groups.manage_members', server=server, group=group.name, type=type, invite=invite, player=member.name, ext=ext)), 303
        abort(404)
    abort(403)