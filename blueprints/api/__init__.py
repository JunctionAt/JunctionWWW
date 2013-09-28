from . import docs, apikey_model
from flask import request, Blueprint
from blueprints.api.apikey_model import ApiKey

blueprint = Blueprint('api', __name__, template_folder='templates')


def require_api_key(write=True, access=None):
    def init(func):
        def wrap(*args, **kwargs):
            try:
                key = ApiKey.objects(key=request.headers['apikey']).first()
                if access and access not in key.access:
                    return {'message': "Api key doesn't have access to this"}
            except KeyError:
                return {'message': "No api key provided in headers"}
            func(*args, **kwargs)
        return wrap
    return init


from docs import *
from views import apikey_settings_pane