"""
As User
-------

Staff may use this endpoint to request cookie authorization as another user.  Alternatively to using cookie
authorization for switching users, a client may include a ``From`` HTTP header with the name of the player
to act as during the context of the request.
"""

from flask import Blueprint, current_app, abort, request, render_template, url_for, session, make_response, g
from flask.ext.principal import RoleNeed, Principal, Identity, PermissionDenied, Permission, identity_loaded
from flask.ext.login import current_user, user_logged_out, logout_user, login_user
from werkzeug.exceptions import Forbidden, BadRequest
from sqlalchemy.orm.exc import NoResultFound
from wtalchemy.orm import model_form
import re

from blueprints.auth import login_required
from blueprints.base import db
from blueprints.auth.user_model import User
from blueprints.player_groups import Group, player_groups
from blueprints.api import apidoc

as_user = Blueprint('as_user', __name__, template_folder='templates')

@apidoc(__name__, as_user, '/as/<player>.json', endpoint='switch_user', defaults=dict(ext='json'), methods=('PUT',))
def switch_user_put_api(player, ext):
    """
    Sets a cookie that allows a staff member to perform operations as ``player``.
    """

@apidoc(__name__, as_user, '/as/<player>.json', endpoint='switch_user', defaults=dict(ext='json'), methods=('DELETE',))
def switch_user_delete_api(player, ext):
    """
    If a staff member is currently switched to ``player``, this request will reset the session cookie back to the original player.
    Has the same effect as a PUT request to /as/``original_player_name``.json
    """

@as_user.route('/as/<player>', defaults=dict(ext='html'), methods=('PUT','DELETE'))
@login_required
def switch_user(player, ext):
    if request.method =='DELETE' and not player == current_user.name:
        return redirect(url_for('as_user.switch_user', player=current_user.name, ext=ext)), 302
    resp = make_response(redirect(url_for('player_profiles.show_profile', player=player, ext=ext)), 303)
    original_user = session.pop('original_user', None)
    resp.set_cookie('original_user', None)
    if original_user:
        try: login_user(db.session.query(User).filter(User.name==original_user).one())
        except NoResultFound:
            logout_user()
            abort(500)
    if request.method == 'DELETE': return resp
    try:
        with Permission(RoleNeed('as_user')).require(403): pass
        user = db.session.query(User).filter(User.name==player).one()
        if not user.name == player:
            return redirect(url_for('as_user.switch_user', player=user.name, ext=ext)), 301
        resp = make_response(redirect(url_for('player_profiles.show_profile', player=player, ext=ext)), 303)
        session['original_user'] = current_user.name            
        resp.set_cookie('original_user', current_user.name)
        login_user(user)
        return resp
    except NoResultFound:
        abort(404)

@identity_loaded.connect_via(current_app._get_current_object())
def on_identity_loaded(sender, identity, **_):
    """Enable user switching without cookies"""
    
    try:
        player = request.headers['From']
        if current_user.name == player: return
        if not identity.can(Permission(RoleNeed('as_user'))):
            raise PermissionDenied()
        user = db.session.query(User).filter(User.name==player).one()
        login_user(user)
    except KeyError:
        pass
    except NoResultFound:
        @after_this_request
        def get_response(response):
            return BadRequest().get_response(dict())
        logout_user()
        abort()
        pass
    except PermissionDenied:
        @after_this_request
        def get_response(response):
            return Forbidden().get_response(dict())
        logout_user()
        abort()

@user_logged_out.connect_via(current_app._get_current_object())
def on_user_logged_out(sender, user, **_):
    if session.get('original_user'):
        del session['original_user']

def after_this_request(func):
    if not hasattr(g, 'call_after_request'):
        g.call_after_request = []
    g.call_after_request.append(func)
    return func

@current_app.after_request
def per_request_callbacks(response):
    for func in getattr(g, 'call_after_request', ()):
        response = func(response)
    return response
