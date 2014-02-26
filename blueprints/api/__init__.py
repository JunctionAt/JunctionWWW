__author__ = 'HansiHE'

from . import docs, apikey_model
from flask import request, Blueprint
from blueprints.api.apikey_model import ApiKey
from blueprints.auth import current_user
from blueprints.auth.user_model import User
from blueprints.auth.util import validate_username
from functools import wraps

datetime_format = "%I:%M %d/%m/%Y %p"

blueprint = Blueprint('api', __name__, template_folder='templates')

access_tokens = dict()


def register_api_access_token(token, description=None, link=None, permission=None):
    access_tokens[token] = dict(token=token, description=description, link=link, permission=permission)


def require_api_key(required_access_tokens=list(), allow_user_permission=False, asuser_must_be_registered=True):
    def init(func):
        @wraps(func)
        def wrap(*args, **kwargs):

            # If allow_user_permission is True, make sure the user has the appropriate permissions.
            if allow_user_permission:
                allowed = True
                for token in required_access_tokens:
                    if not current_user.has_permission(access_tokens[token]['permission']):
                        allowed = False
                if allowed:
                    request.api_user = current_user
                    request.api_user_name = current_user.name
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
            if 'AsUser' in request.headers:
                if 'api.as_user' not in key.access:
                    return {'error': [{'message': "api key doesn't have access to 'api.as_user', required for using the AsUser header", 'identifier': "permission#api.as_user"}]}

                username = request.headers['AsUser']

                # Make sure the username format is valid
                if not validate_username(username):
                    return {'error': [{'message': "the AsUser username is not a valid minecraft username", 'identifier': "asuser_username_not_valid"}]}

                # Obtain user from db
                user = User.objects(name=username).first()
                if user is None and asuser_must_be_registered:
                    return {'error': [{'message': "the user specified in the AsUser header wasn't found", 'identifier': "asuser_not_found"}]}

                request.api_user = user
                request.api_user_name = username

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
