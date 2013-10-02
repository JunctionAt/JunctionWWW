__author__ = 'HansiHE'

from flask import request
from blueprints.api import require_api_key, register_api_access_token
from blueprints.base import rest_api
from flask.ext.restful import Resource
from flask.ext.restful.reqparse import RequestParser
from ..user_model import ConfirmedUsername

add_api_username_verification_token = 'api.auth.add_ip_username_verification'


def check_verification(username, ip):
    return ConfirmedUsername.objects(ip=str(ip), username__iexact=username).first() is not None
    #TODO: Check time


def add_verification(username, ip):
    confirmed = ConfirmedUsername(ip=ip, username=username)
    confirmed.save()


class IpUsernameVerification(Resource):

    get_parser = RequestParser()
    get_parser.add_argument("username", type=str, required=True)

    def get(self):
        args = self.get_parser.parse_args()

        result = check_verification(args.get("username"), request.remote_addr)

        return {'verified': result}

    put_parser = RequestParser()
    put_parser.add_argument("username", type=str, required=True)
    put_parser.add_argument("ip", type=str, required=True)

    @require_api_key(access_tokens=[add_api_username_verification_token])
    def put(self):
        args = self.put_parser.parse_args()

        add_verification(args.get("username"), args.get("ip"))

        return {'success': True}


rest_api.add_resource(IpUsernameVerification, '/auth/ip_username_verification')
register_api_access_token(add_api_username_verification_token,
                          """Authenticates a username with an ip address. This would enable the user to register from that IP.""", permission="api.auth.add_ip_username_verification")
