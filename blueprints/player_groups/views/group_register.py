__author__ = 'HansiHE'

import flask_login
from flask import render_template, jsonify, request, current_app, abort, flash, redirect, url_for
from werkzeug.datastructures import MultiDict
from mongoengine import *
import re

from blueprints.auth import login_required
from blueprints.api import apidoc
from blueprints.player_groups.group_model import Group

from blueprints.player_groups import player_groups

@apidoc(__name__, player_groups, '/<server>/groups/register.json', endpoint='register_group', defaults=dict(ext='json'), methods=('POST',))
def register_group_api(server, group, ext):
    """
    Register a new group using fields from the request body.

    The request must include a ``display_name`` field and at least one ``invited_members`` or ``invited_owners`` that is not the player making the request.
    The request may include any other fields returned in the /<server>/group/<group>.json endpoint.
    """

@login_required
def register_group(server, ext):
    """Register group"""

    try:
        self = player_groups[server]
    except KeyError:
        abort(404)
    group = Group()
    user = flask_login.current_user
    form = self.GroupRegisterForm(MultiDict(request.json) or request.form, group, csrf_enabled=False)
    if request.method == 'POST' and form.validate() & self.validate_members(form, user):
        form.populate_obj(group)
        # Make ownership and membership mutually exclusive
        group.invited_owners = list(set(group.invited_owners + [user]))
        group.invited_members = list(set(group.invited_members) - set(group.invited_owners))
        # Registree is a confirmed owner
        group.owners = [ user ]
        group.display_name = re.sub(r'\s+', ' ', group.display_name.strip())
        group.server = self.server
        group.name = re.sub(r'\s+', '_', re.sub(r'[^a-zA-Z0-9]+', '', group.display_name))
        group.id = "%s.pending.%s"%(self.server, group.name)
        # Delete any pending group registrations of the same id
        Group.objects(id=group.id).remove()
        #manage_notifications(group) #TODO: Notifications!!
        # Commit
        group.save()
        # Done
        if ext == 'html': flash('%s registration complete pending confirmation by other %s.'%(self.group.capitalize(), self.members))
        return redirect(url_for('player_groups.show_group', server=server, group=group.name, ext=ext)), 303
    if ext == 'json': return jsonify(
        fields=reduce(lambda errors, (name, field):
        errors if not len(field.errors) else errors + [dict(name=name, errors=field.errors)],
            form._fields.iteritems(),
            list())), 400
    return render_template('edit_group.html', endpoint=self, form=form, register=True)