__author__ = 'HansiHE'

import flask_login
from flask import render_template, jsonify, request, current_app, abort, flash, redirect, url_for

from blueprints.auth import login_required
from blueprints.api import apidoc

from blueprints.player_groups import player_groups

@apidoc(__name__, player_groups, '/<server>/groups/invitations.json', endpoint='show_invitations', defaults=dict(ext='json'))
def show_invitations_api(server, group, ext):
    """List the current player's group invitations on ``server``.

    Eg.:

    .. code-block::

       {
           "invitations": [
               {
                   "name": "Moo",
                   "role": "citizen"
               }
           ]
       }
    """

@login_required
def show_invitations(server, ext):
    try:
        self = player_groups[server]
    except KeyError:
        abort(404)
    if ext == 'json':
        n=[]
        owner = self.invited_owner_of(flask_login.current_user)
        if len(owner): n += map(lambda group: dict(role=self.owner, name=group.name), owner)
        member = self.invited_member_of(flask_login.current_user)
        if len(member): n += map(lambda group: dict(role=self.member, name=group.name), member)
        return jsonify(invitations=n)
    return render_template('show_invitations.html', endpoint=self)
