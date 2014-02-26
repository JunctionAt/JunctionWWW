__author__ = 'HansiHE'

from .. import require_api_key
from blueprints.base import rest_api
from flask.ext.restful import Resource
from blueprints.api import register_api_access_token


class ApiTest(Resource):

    @require_api_key(required_access_tokens=['api.test'])
    def get(self):
        return {'success': True}

    @require_api_key(required_access_tokens=['api.test'])
    def post(self):
        return {'success': True}

rest_api.add_resource(ApiTest, '/test')
register_api_access_token('api.test',
                          """Provides access to the method /test. As indicated by the name, doesn't do anything at all.""")