from . import docs, apikey_model
from flask import request, Blueprint
from blueprints.api.apikey_model import ApiKey
from blueprints.auth.user_model import User

datetime_format = "%S:%M %d/%m/%Y %Z"

blueprint = Blueprint('api', __name__, template_folder='templates')

access_tokens = dict()

def register_api_access_token(token, description=None, link=None, permission=None):
    access_tokens[token] = dict(token=token, description=description, link=link, permission=permission)


def require_api_key(access_tokens=list()): # I know, not a word
    def init(func):
        def wrap(*args, **kwargs):

            try:
                key = ApiKey.objects(key=request.headers['ApiKey']).first()
                for access in access_tokens:
                    if access not in key.access:
                        return {'error': [{'message': "api key doesn't have access to '%s'" % access, 'identifier': "permission#%s" % access}]}
            except KeyError:
                return {'error': [{'message': "no/invalid ApiKey header provided", 'identifier': "apikey_not_provided"}]}

            if 'AsUser' in request.headers:
                if 'api.as_user' not in key.access:
                    return {'error': [{'message': "api key doesn't have access to 'api.as_user', required for using the AsUser header", 'identifier': "permission#api.as_user"}]}

                user = User.objects(name=request.headers['AsUser']).first()
                if user is None:
                    return {'error': [{'message': "the user specified in the AsUser header wasn't found", 'identifier': "asuser_not_found"}]}

                request.api_user = user

            else:
                request.api_user = key.owner

            return func(*args, **kwargs)
        return wrap
    return init

register_api_access_token("api.as_user", "allows you to use the AsUser header to perform actions as users other than the key creator", permission="api.as_user")


from docs import *
from views import apikey_settings_pane, apikey_api