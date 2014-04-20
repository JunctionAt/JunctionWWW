from blueprints import uuid_utils
from models.player_model import MinecraftPlayer

__author__ = 'HansiHE'

from flask import request
from flask.ext.restful import Resource
from flask.ext.restful.reqparse import RequestParser
import re
import datetime

from blueprints.api import require_api_key, register_api_access_token, datetime_format
from blueprints.base import rest_api
from models.ban_model import Ban
from blueprints.auth.util import validate_username
from models.servers_model import Server


class InvalidDataException(Exception):
    pass


def get_local_bans(uuid=None, uid=None, active=None):
    query = dict()

    if uuid is not None:
        query['target'] = uuid
    if uid is not None:
        query['uid'] = uid
    if active is not None:
        query['active'] = active

    bans_data = Ban.objects(**query)

    bans_response = []
    for ban_data in bans_data:
        bans_response.append(construct_local_ban_data(ban_data))

    return bans_response


def construct_local_ban_data(ban):
    return dict(
        id=ban.uid, issuer_old=ban.issuer, username=ban.username, reason=ban.reason,
        server=ban.server,
        time=ban.time.strftime(datetime_format) if ban.time is not None else None,
        active=ban.active,
        remove_time=ban.removed_time.strftime(datetime_format) if ban.removed_time is not None else None,
        remove_user=ban.removed_by, source='local')


def get_global_bans(uuid):
    return [] #Not implemented


def get_bans(uuid=None, uid=None, active=None, scope="local"):
    """

    :param username:
    :param uid:
    :param active: none if both
    :param scope: local, global or full
    :return: array of bans
    """

    bans_raw = list()

    if scope == 'local' or scope == 'full':
        bans_raw += get_local_bans(uuid=uuid, uid=uid, active=active)
    elif scope == 'global' or scope == 'full':
        bans_raw += get_global_bans(uuid=uuid)

    return bans_raw


class Bans(Resource):
    get_parser = RequestParser()
    get_parser.add_argument("username", type=str)  # TODO: Temporary
    get_parser.add_argument("uuid", type=str)
    get_parser.add_argument("id", type=int)
    get_parser.add_argument("active", type=str, default="true", choices=["true", "false", "none"])
    get_parser.add_argument("scope", type=str, default="local", choices=["local", "global", "full"])

    def validate_get(self, args):
        if not (args.get("username") and validate_username(args.get("username"))) and not args.get("id"):
            return {'error': [{"message": "an id or a uuid must be provided"}]}

        if args.get("id") and args.get("scope") != "local":
            return {'error': [{"message": "query by id can only be used in local scope"}]}

        if args.get("active") == "False" and args.get("scope") != "local":
            return {'error': [{"message": "query for non active bans can only be used in local scope"}]}

    def temp_get_uuid_from_mcname(self, mcname):  #TODO: Remove
        player = MinecraftPlayer.objects(mcname__iexact=mcname).first()
        if player is not None:
            return player.uuid

    @require_api_key(required_access_tokens=['anathema.bans.get'], asuser_must_be_registered=False)
    def get(self):
        args = self.get_parser.parse_args()
        validate_args = self.validate_get(args)
        if validate_args:
            return validate_args

        uuid = args.get("uuid") or self.temp_get_uuid_from_mcname(args.get("username"))
        uid = args.get("id")
        active_str = args.get("active")
        active = None
        if active_str != 'none':
            if active_str == 'true':
                active = True
            elif active_str == 'false':
                active = False
        scope = args.get("scope")

        bans = get_bans(uuid, uid, active, scope)

        return {'bans': bans}

    post_parser = RequestParser()
    post_parser.add_argument("username", type=str, required=True)  # Username to ban
    post_parser.add_argument("uuid", type=str)
    post_parser.add_argument("reason", type=str, required=True)  # A optional reason for the ban
    post_parser.add_argument("server", type=str, required=True)  # A optional server/interface where the ban was made
    # Issuer is provided in as_user

    def validate_post(self, args):
        if args.get("username") and not validate_username(args.get("username")):
            return {'error': [{"message": "invalid username"}]}

        if args.get("reason") and len(args.get("reason")) > 1000:
            return {'error': [{"message": "the reason must be below 1000 characters long"}]}

        if args.get("server") and Server.verify_fid(args.get("server")): #len(args.get("server")) > 100:
            return {'error': [{"message": "the server field must be a valid fid"}]}

    @require_api_key(required_access_tokens=['anathema.bans.post'])
    def post(self):
        args = self.post_parser.parse_args()
        validate_args = self.validate_post(args)
        if validate_args:
            return validate_args

        issuer = request.api_user
        username = args.get("username")
        reason = args.get("reason")
        source = args.get("server")
        uuid = args.get("uuid") or uuid_utils.lookup_uuid(username)  # TODO: Remove on 1.8

        player = MinecraftPlayer.find_or_create_player(uuid, username)

        if len(Ban.objects(username=username, active=True)) > 0:
            return {
                'error': [{'message': "the user is already banned", 'identifier': "anathema.bans.add:user_already_exists"}]}

        ban = Ban(issuer=issuer, issuer_old=issuer.name, target=player, username=username, reason=reason, server=source).save()

        return {'ban': construct_local_ban_data(ban)}


    delete_parser = RequestParser()
    delete_parser.add_argument("username", type=str)
    delete_parser.add_argument("id", type=int)

    def validate_delete(self, args):
        if not args.get("username") and not args.get("id"):
            return {"message": "a id or a username must be provided"}

    @require_api_key(required_access_tokens=['anathema.bans.delete'], asuser_must_be_registered=False)
    def delete(self):
        args = self.delete_parser.parse_args()
        validate_args = self.validate_delete(args)
        if validate_args:
            return validate_args

        remover = request.api_user_name
        username = args.get("username")
        uid = args.get("id")

        query = dict(active=True)

        if username:
            query["username"] = username
        if uid:
            query["uid"] = uid

        ban = Ban.objects(**query).first()

        ban.active = False
        ban.removed_by = remover
        ban.removed_time = datetime.datetime.utcnow()
        ban.save()

        return {'ban': construct_local_ban_data(ban)}


rest_api.add_resource(Bans, '/anathema/bans')

register_api_access_token('anathema.bans.get')
register_api_access_token('anathema.bans.post', permission="api.anathema.bans.post")
register_api_access_token('anathema.bans.delete', permission="api.anathema.bans.delete")