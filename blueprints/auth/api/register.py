__author__ = 'HansiHE'

from flask import request
from flask.ext.restful import Resource
from flask.ext.restful.reqparse import RequestParser

from blueprints.api import require_api_key, register_api_access_token
from blueprints.base import rest_api
from blueprints import uuid_utils
from blueprints.auth.util import check_authenticated_ip, add_authenticated_ip

add_api_username_verification_token = 'api.auth.add_ip_username_verification'


class IpUsernameVerification(Resource):

    get_parser = RequestParser()
    get_parser.add_argument("username", type=str)
    get_parser.add_argument("uuid", type=str)

    def get(self):
        args = self.get_parser.parse_args()

        result = check_authenticated_ip(request.remote_addr, username=args.get("username"), uuid=args.get("uuid"))

        return {'verified': result is not None}

    put_parser = RequestParser()
    put_parser.add_argument("username", type=str, required=True)
    put_parser.add_argument("ip", type=str, required=True)
    put_parser.add_argument("uuid", type=str, required=True)

    @require_api_key(required_access_tokens=[add_api_username_verification_token])
    def put(self):
        args = self.put_parser.parse_args()

        add_authenticated_ip(args.get("username"), args.get("uuid"), args.get("ip"))

        return {'success': True}


rest_api.add_resource(IpUsernameVerification, '/auth/ip_username_verification')
register_api_access_token(add_api_username_verification_token,
                          """Authenticates a username with an ip address. This would enable the user to register from that IP.""", permission="api.auth.add_ip_username_verification")
