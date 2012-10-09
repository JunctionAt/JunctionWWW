"""
As User
-------

Staff may use this endpoint to request cookie authorization as another user.  As an alternative to using cookie
authorization for switching users, a client may include a ``From`` HTTP header with the name of the player
to act as during the context of the request.
"""

from flask import Blueprint, current_app, abort, request, render_template, url_for, session, make_response, g, redirect
from flask.ext.principal import UserNeed, RoleNeed, Principal, Identity, PermissionDenied, Permission, identity_changed
from flask.ext.login import current_user, user_logged_out, logout_user, login_user
from werkzeug.exceptions import Forbidden, BadRequest, NotFound, InternalServerError
from sqlalchemy.orm.exc import NoResultFound
from wtalchemy.orm import model_form
import re

from blueprints.auth import login_required
from blueprints.base import db
from blueprints.auth.user_model import User
from blueprints.player_groups import Group, player_groups
from blueprints.api import apidoc
from blueprints.roles import identity_roles

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
    try:
        response = None
        try:
            original_user = db.session.query(User).filter(User.name==session['original_user']).one()
            if not identity_roles(Identity(original_user.name)).can(Permission(RoleNeed('as_user'))):
                raise PermissionDenied()
            # User with previous authorization via original_user
            if request.method == 'DELETE' and player == current_user.name:
                target = current_user.name
            elif request.method == 'PUT' and player == original_user.name:
                target = original_user.name
            if target and not player == target:
                return redirect(redirect(url_for('as_user', player=target, ext=ext))), 301
            elif target:
                # Returning to normal
                login_user(original_user)
                response = make_response(redirect(url_for('player_profiles.show_profile', player=original_user.name, ext=ext)), 303)
            elif request.method == 'DELETE':
                return redirect(url_for('as_user.switch_user', player=current_user.name, ext=ext)), 307
            else:
                # User attempting a switch while already switched
                login_user(original_user)
                raise KeyError()
        except KeyError:
            Permission(RoleNeed('as_user')).require(403)
            if request.method == 'DELETE': abort(403)
            # User without original_user, or, user just switched to original_user with an additional switch necessary
            user = db.session.query(User).filter(User.name==player).one()
            if not player == user.name:
                return redirect(redirect(url_for('as_user', player=user.name, ext=ext))), 301
            response = make_response(redirect(url_for('player_profiles.show_profile', player=player, ext=ext)), 303)
            response.set_cookie('original_user', current_user.name)
            session['original_user'] = current_user.name
            login_user(user)
            return response
    except NoResultFound:
        response = Forbidden().get_response(dict())
    except PermissionDenied:
        response = Forbidden().get_response(dict())
    response.set_cookie('original_user', '')
    del session['original_user']
    return response

@identity_changed.connect_via(current_app._get_current_object())
def on_identity_changed(sender, identity, **_):
    """
    Enable user switching without cookies.

    I don't think signals are meant to influence the response, so abort() doesn't
    actually prevent the request from going through.

    In those cases where we should abort the request, set up an after_request hook
    to intercept the broken response.
    """
    
    try:
        player = request.headers['From']
        if current_user.name == player: return
        with identity.require(Permission(RoleNeed('as_user'))): pass
        user = db.session.query(User).filter(User.name==player).one()
        login_user(user)
    except NoResultFound:
        @after_this_request
        def get_response(response):
            return BadRequest().get_response(dict())
        logout_user()
        abort()
    except PermissionDenied:
        @after_this_request
        def get_response(response):
            return Forbidden().get_response(dict())
        logout_user()
        abort()
    except KeyError:
        pass

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

@current_app.context_processor
def inject_identity():
    return dict(can_switch=can_switch, get_original_user=get_original_user, Permission=Permission, RoleNeed=RoleNeed, UserNeed=UserNeed)

def can_switch():
    if Permission(RoleNeed('as_user')).can(): return True
    return True and session.get('original_user', False)

def get_original_user():
    if not hasattr(g, 'roles_original_user'):
        if session.get('original_user', None):
            g.roles_original_user = db.session.query(User).filter(User.name==session['original_user']).one()
        else:
            g.roles_original_user = None
    return g.roles_original_user
