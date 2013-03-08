__author__ = 'HansiHE'

import flask_login
from flask import render_template, jsonify, request, current_app, abort, flash, redirect, url_for

from blueprints.auth import login_required
from blueprints.api import apidoc
from blueprints.player_groups.group_model import Group

from blueprints.player_groups import player_groups

@apidoc(__name__, player_groups, '/<server>/group/<group>/leave.json', endpoint='leave_group', defaults=dict(ext='json'), methods=('POST',))
def leave_group_api(server, group, ext):
    """
    Used by the current player to give up membership of ``group``.
    """

@login_required
def leave_group(server, group, ext):
    try:
        self = player_groups[server]
    except KeyError:
        abort(404)
    name = group
    group = Group.objects(gid__in=[
        "%s.%s"%(self.server,name),
        "%s.pending.%s"%(self.server,name)
    ]).first()
    if group is None:
        abort(404)
    user = flask_login.current_user
    if not group.name == name:
        # Redirect to preferred caps
        return redirect(url_for('player_groups.leave_group', server=server, group=group.name, ext=ext)), 301
    if user in group.members or user in group.owners:
        if request.method == 'POST':
            group.owners = list(set(group.owners) - set([user]))
            group.members = list(set(group.members) - set([user]))
            group.invited_owners = list(set(group.invited_owners) - set([user]))
            group.invited_members = list(set(group.invited_members) - set([user]))
            group.member_count -= 1
            group.save()
            if ext == 'html': flash("You are no longer %s of %s."%(group.a_member, group.display_name))
            return redirect(url_for('player_groups.show_group', server=server, group=group.name, ext=ext)), 303
        return render_template('leave_group.html', endpoint=self, group=group)
    abort(403)


@apidoc(__name__, player_groups, '/<server>/group/<group>/join.json', endpoint='join_group', defaults=dict(ext='json'), methods=('POST',))
def join_group_post_api(server, group, ext):
    """
    Used by the current player to join ``group``.

    If ``group`` is not public, the player must have been invited to join.
    """

@apidoc(__name__, player_groups, '/<server>/group/<group>/join.json', endpoint='join_group', defaults=dict(ext='json'), methods=('DELETE',))
def join_group_delete_api(server, group, ext):
    """
    Used by the current player to decline an invitation to join ``group``.
    """

@login_required
def join_group(server, group, ext):
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
    user = flask_login.current_user
    if not group.name == name:
        # Redirect to preferred caps
        return redirect(url_for('player_groups.join_group', server=server, group=group.name, ext=ext)), 301
    if not user in group.members and not user in group.owners:
        if request.method in ('POST', 'DELETE'):
            if request.method == 'POST':
                # Join action
                if not group.public and user in group.invited_owners:
                    group.owners.append(user)
                elif group.public or user in group.invited_members:
                    group.members.append(user)
                    # Maintain invited status for members of public groups
                    group.invited_members = list(set(group.invited_members + [user]))
                else:
                    abort(403)
                    # Check for confirmation of group registration
                if group.gid == "%s.pending.%s"%(self.server,group.name):
                    group = Group.confirm(group)
                    del(group)
                if ext == 'html': flash("You have joined %s."%group.display_name)
            else:
                # Pass action
                if user in group.invited_owners:
                    group.invited_owners = list(set(group.invited_owners) - set([user]))
                elif user in group.invited_members:
                    group.invited_members = list(set(group.invited_members) - set([user]))
                else:
                    abort(403)
                if ext == 'html': flash("Invitation to %s declined."%group.display_name)
            group.member_count += 1
            #manage_notifications(group) #TODO: Notifications!!
            # Commit
            group.save()
            return redirect(url_for('player_groups.show_group', server=server, group=group.name, ext=ext)), 303
        return render_template('join_group.html', endpoint=self, group=group)
    abort(403)