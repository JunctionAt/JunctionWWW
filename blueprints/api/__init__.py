from models.player_model import MinecraftPlayer

__author__ = 'HansiHE'

from flask import request, Blueprint
from functools import wraps

from . import docs
from models.apikey_model import ApiKey
from blueprints.auth import current_user
from models.user_model import User
from blueprints.auth.util import validate_username


datetime_format = "%I:%M %d/%m/%Y %p"

blueprint = Blueprint('api', __name__, template_folder='templates')

access_tokens = dict()


def register_api_access_token(token, description=None, link=None, permission=None):
    access_tokens[token] = dict(token=token, description=description, link=link, permission=permission)


import flask_wtf.csrf as csrf


def _check_user_permission(required_tokens, user):
    if "CSRF" not in request.headers:
        return False
    if not csrf.validate_csrf(request.headers.get("CSRF")):
        return False

    print("ya")

    for token in required_tokens:
        print(token)
        print(access_tokens[token])
        if not user.has_permission(access_tokens[token]['permission']):
            return False

    print("yaa")
    request.api_user = current_user
    request.api_user_name = current_user.name
    return True


def require_api_key(required_access_tokens=list(), allow_user_permission=False, asuser_must_be_registered=True):
    """

    :param required_access_tokens:
    :param allow_user_permission: Allow users to use this by simply having the right permissions. This requires that a CSRF header is sent with a valid CSRF token.
    :param asuser_must_be_registered:
    :return:
    """

    def init(func):
        @wraps(func)
        def wrap(*args, **kwargs):

            # If allow_user_permission is True, make sure the user has the appropriate permissions.
            if allow_user_permission and _check_user_permission(required_access_tokens, current_user):
                return func(*args, **kwargs)

            # Check and obtain API key from DB
            try:
                key = ApiKey.objects(key=request.headers['ApiKey']).first()
            except KeyError:
                return {'error': [{'message': "no/invalid ApiKey header provided", 'identifier': "apikey_not_provided"}]}
            if key is None:
                return {'error': [{'message': "no/invalid ApiKey header provided", 'identifier': "apikey_not_provided"}]}
            for access in required_access_tokens:
                if access not in key.access:
                    return {'error': [{'message': "api key doesn't have access to '%s'" % access, 'identifier': "permission#%s" % access}]}

            # Check for the AsUser header, apply stuff to context
            if 'AsUser' in request.headers or 'AsPlayer' in request.headers:
                if 'api.as_user' not in key.access:
                    return {'error': [{'message': "api key doesn't have access to 'api.as_user', required for using the AsUser and AsPlayer headers", 'identifier': "permission#api.as_user"}]}

                if 'AsUser' in request.headers:
                    username = request.headers['AsUser']

                    # Obtain user from db
                    user = User.get_user_by_username(username)
                    if user is None and asuser_must_be_registered:
                        return {'error': [{'message': "the user specified in the AsUser header wasn't found", 'identifier': "asuser_not_found"}]}

                    request.api_user = user
                    request.api_user_name = username
                elif 'AsPlayer' in request.headers:
                    uuid = request.headers['AsPlayer']

                    player = MinecraftPlayer.find_player(uuid)
                    if player is None:
                        return {'error': [{'message': "player uuid specified in AsPlayer header is not registered in database (has not logged in?)", 'identifier': "player_uuid_not_found"}]}

                    user = User.get_user_by_uuid(player)
                    if user is None and asuser_must_be_registered:
                        return {'error': [{'message': "the uuid specified in the AsPlayer field is not owned by a website user", 'identifier': "asuser_not_found"}]}

                    request.api_user = user
                    request.api_user_name = user.name
                    request.api_player = player
            else:
                request.api_user = key.owner
                request.api_user_name = key.owner.name

            return func(*args, **kwargs)
        return wrap
    return init


def endpoint():
    """
    This decorator adds documentation for the endpoint.
    It does nothing for now, but it is good practice to add this to views.
    """
    def wrap(func):
        # TODO: Add documentation stuff
        return func
    return wrap

register_api_access_token("api.as_user", "allows you to use the AsUser header to perform actions as users other than the key creator", permission="api.as_user")


from docs import *
from views import apikey_settings_pane, apikey_api
