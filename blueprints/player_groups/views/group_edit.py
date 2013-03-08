__author__ = 'HansiHE'

import flask_login
from flask import render_template, jsonify, request, current_app, abort, flash, redirect, url_for
from werkzeug.datastructures import MultiDict
from mongoengine import *

from blueprints.auth import login_required
from blueprints.auth.user_model import User
from blueprints.api import apidoc
from blueprints.player_groups.group_model import Group

from blueprints.player_groups import player_groups

@apidoc(__name__, player_groups, '/<server>/group/<group>.json', endpoint='edit_group', defaults=dict(ext='json'), methods=('POST',))
def edit_group_post_api(server, group, ext):
    """Edit info for ``group`` using new fields from the request body.

    In additon to the fields returned by the /<server>/group/<group>.json endpoint,
    membership and ownership of this group can be set en masse by providing
    a list of player names as the new values for ``invited_members`` or ``invited_owners``.
    The ``display_name`` of a group cannot be changed.
    """

@login_required
def edit_group(server, group, ext):
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
        return redirect(url_for('player_groups.edit_group', server=server, group=group.name, ext=ext)), 301
    user = flask_login.current_user
    if not user in group.owners: abort(403)
    data = MultiDict(request.json) or request.form
    form = self.GroupEditForm(data, group, csrf_enabled=False)
    if request.method == 'POST' and form.validate() & self.validate_members(form, user):
        form.populate_obj(group)
        # Make ownership and membership mutually exclusive
        group.invited_owners = list(set(group.invited_owners + [user]))
        group.invited_members = list(set(group.invited_members) - set(group.invited_owners))
        # Remove uninvited players, promote & demote
        promotions = set(group.invited_owners) & set(group.members)
        demotions = set(group.invited_members) & set(group.owners)
        group.owners = list(promotions | (set(group.owners) & set(group.invited_owners)))
        group.members = list(demotions | (set(group.members) & set(group.invited_members)))
        group.member_count = len(group.owners) + len(group.members)
        # Send notifications
        #manage_notifications(group) #TODO: Notifications!!
        # Commit
        group.save()
        # Done
        if ext == 'html': flash('%s saved'%self.group.capitalize())
        return redirect(url_for('player_groups.edit_group', server=server, group=group.name, ext=ext)), 303
    if ext == 'json': return jsonify(
        fields=reduce(lambda errors, (name, field):
        errors if not len(field.errors) else errors + [dict(name=name, errors=field.errors)],
            form._fields.iteritems(),
            list())), 400
    return render_template('edit_group.html', endpoint=self, form=form, group=group)