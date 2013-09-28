__author__ = 'HansiHE'

from flask import request
from flask.ext.restful import Resource
from flask.ext.restful.reqparse import RequestParser
from blueprints.auth import current_user
from blueprints.api import require_api_key, register_api_access_token, datetime_format
from blueprints.base import rest_api
from ..ban_model import Ban
import datetime


class InvalidDataException(Exception):
    pass


def get_local_bans(username=None, uid=None, active=None):
    query = dict()

    if username is not None:
        query['username'] = username
    if uid is not None:
        query['uid'] = uid
    if active is not None:
        query['active'] = active

    bans_data = Ban.objects(**query)

    bans_response = []
    for ban_data in bans_data:
        bans_response.append(dict(
            id=ban_data.uid, issuer=ban_data.issuer, username=ban_data.username, reason=ban_data.reason,
            server=ban_data.server,
            time=ban_data.time.strftime(datetime_format) if ban_data.time is not None else None,
            active=ban_data.active,
            remove_time=ban_data.removed_time.strftime(datetime_format) if ban_data.removed_time is not None else None,
            remove_user=ban_data.removed_by, source='local'))

    return bans_response


def get_global_bans(username):
    return [] #Not implemented


def get_bans(username=None, uid=None, active=None, scope="local"):
    """

    :param username:
    :param uid:
    :param active: none if both
    :param scope: local, global or full
    :return: array of bans
    """

    bans_raw = list()

    if scope == 'local' or scope == 'full':
        bans_raw += get_local_bans(username=username, uid=uid, active=active)
    elif scope == 'global' or scope == 'full':
        bans_raw += get_global_bans(username=username)

    return bans_raw


class Bans(Resource):

    get_parser = RequestParser()
    get_parser.add_argument("username", type=str)
    get_parser.add_argument("id", type=int)
    get_parser.add_argument("active", type=str, default="true", choices=["true", "false", "none"])
    get_parser.add_argument("scope", type=str, default="local", choices=["local", "global", "full"])

    def validate_get(self, args):
        if not args.get("username") and not args.get("id"):
            return {'error': [{"message": "a id or a username must be provided"}]}, 400

        if args.get("id") and args.get("scope") != "local":
            return {'error': [{"message": "query by id can only be used in local scope"}]}

        if args.get("active") == "False" and args.get("scope") != "local":
            return {'error': [{"message": "query for non active bans can only be used in local scope"}]}

    @require_api_key(access_tokens=['anathema.bans.get'])
    def get(self):
        args = self.get_parser.parse_args()
        validate_args = self.validate_get(args)
        if validate_args:
            return validate_args

        username = args.get("username")
        uid = args.get("id")
        active_str = args.get("active")
        active = None
        if active_str != 'none':
            if active_str == 'true':
                active = True
            elif active_str == 'false':
                active = False
        scope = args.get("scope")

        bans = get_bans(username, uid, active, scope)

        print(request.api_user)

        return {'bans': bans}

    post_parser = RequestParser()
    post_parser.add_argument("username", type=str, required=True) # Username to ban
    post_parser.add_argument("issuer", type=str, required=True) # The one who created the ban, this is optional and requires extra permissions
    post_parser.add_argument("reason", type=str, required=True) # A optional reason for the ban
    post_parser.add_argument("location", type=str, required=True) # A optional server/interface where the ban was made

    def validate_post(self, args):
        if args.get("username") and len(args.get("username")) > 16:
            return {"message": "usernames are limited to 16 characters (username)"}, 400

        if args.get("issuer") and len(args.get("issuer")) > 16:
            return {"message": "usernames are limited to 16 characters (issuer)"}, 400
        if not args.get("issuer"):
            args["issuer"] = current_user.name

        if args.get("reason") and len(args.get("reason")) > 1000:
            return {"message": "the reason must be below 1000 characters long"}, 400

        if args.get("location") and len(args.get("location")) > 100:
            return {"message": "the location must be below 100 characters long"}

    def post(self):
        args = self.post_parser.parse_args()
        validate_args = self.validate_post(args)
        if validate_args:
            return validate_args

    delete_parser = RequestParser()
    delete_parser.add_argument("username", type=str)
    delete_parser.add_argument("id", type=int)

    def validate_delete(self, args):
        if not args.get("username") and not args.get("id"):
            return {"message": "a id or a username must be provided"}, 400

    def delete(self):
        args = self.delete_parser.parse_args()
        validate_args = self.validate_delete(args)
        if validate_args:
            return validate_args

rest_api.add_resource(Bans, '/anathema/bans')

register_api_access_token('anathema.bans.get')