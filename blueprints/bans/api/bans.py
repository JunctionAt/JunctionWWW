from flask.ext.restful import abort
from blueprints import uuid_utils
from models.player_model import MinecraftPlayer

from flask import request
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
import datetime

from blueprints.api import require_api_key, register_api_access_token, datetime_format
from blueprints.base import rest_api
from models.ban_model import Ban
from models.servers_model import Server
import permissions


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
        id=ban.uid, issuer=ban.issuer.name, username=ban.target.mcname, reason=ban.reason,
        target=dict(name=ban.target.mcname, uuid=ban.target.uuid),
        server=ban.server,
        time=ban.time.strftime(datetime_format) if ban.time is not None else None,
        active=ban.active,
        remove_time=ban.removed_time.strftime(datetime_format) if ban.removed_time is not None else None,
        remove_user=ban.removed_by, source='local')


def get_global_bans(uuid):
    return []  # Not implemented


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
    get_parser.add_argument("uuid", type=uuid_utils.uuid_type)
    get_parser.add_argument("id", type=int)
    get_parser.add_argument("active", type=str, default="true", choices=["true", "false", "none"])
    get_parser.add_argument("scope", type=str, default="local", choices=["local", "global", "full"])

    def validate_get(self, args):
        if not args.get("id") and not args.get("uuid"):
            return {'error': [{"message": "an id or a uuid must be provided"}]}

        if args.get("id") and args.get("scope") != "local":
            return {'error': [{"message": "query by id can only be used in local scope"}]}

        if args.get("active") == "False" and args.get("scope") != "local":
            return {'error': [{"message": "query for non active bans can only be used in local scope"}]}

    @require_api_key(required_access_tokens=['anathema.bans.get'])
    def get(self):
        args = self.get_parser.parse_args()
        validate_args = self.validate_get(args)
        if validate_args:
            return validate_args

        uuid = args.get("uuid")
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
    post_parser.add_argument("uuid", type=uuid_utils.uuid_type, required=True)
    post_parser.add_argument("reason", type=str, required=True)  # A optional reason for the ban
    post_parser.add_argument("server", type=str, required=True)  # A optional server/interface where the ban was made
    # Issuer is provided in as_user

    def validate_post(self, args):
        if args.get("reason") and len(args.get("reason")) > 1000:
            return {'error': [{"message": "the reason must be below 1000 characters long"}]}

        if args.get("server") and Server.verify_fid(args.get("server")):
            return {'error': [{"message": "the server field must be a valid fid"}]}

    @require_api_key(required_access_tokens=['anathema.bans.post'])
    def post(self):
        args = self.post_parser.parse_args()
        validate_args = self.validate_post(args)
        if validate_args:
            return validate_args

        issuer = request.api_user
        reason = args.get("reason")
        source = args.get("server")
        uuid = args.get("uuid")

        player = MinecraftPlayer.find_or_create_player(uuid)

        if len(Ban.objects(target=player, active=True)) > 0:
            return {'error': [{'message': "the user is already banned", 'identifier': "anathema.bans.add:user_already_exists"}]}

        ban = Ban(issuer=issuer, issuer_old=issuer.name, target=player, username=player.mcname, reason=reason,
                  server=source, watching=[issuer]).save()

        return {'ban': construct_local_ban_data(ban)}


    delete_parser = RequestParser()
    delete_parser.add_argument("uuid", type=uuid_utils.uuid_type)
    delete_parser.add_argument("id", type=int)

    def validate_delete(self, args):
        if not args.get("uuid") and not args.get("id"):
            return {"message": "a id or a uuid must be provided"}

    @require_api_key(required_access_tokens=['anathema.bans.delete'])
    def delete(self):
        args = self.delete_parser.parse_args()
        validate_args = self.validate_delete(args)
        if validate_args:
            return validate_args

        remover = request.api_user.name
        uuid = args.get("uuid")
        uid = args.get("id")

        query = dict(active=True)

        if uuid:
            query["target"] = uuid
        if uid:
            query["uid"] = uid

        ban = Ban.objects(**query).first()

        if ban is None:
            return {'error': [{'message': "no active bans found"}]}

        ban.active = False
        ban.removed_by = remover
        ban.removed_time = datetime.datetime.utcnow()
        ban.save()
        ban.ban_lifted()

        return {'ban': construct_local_ban_data(ban)}


class WatchBan(Resource):

    @require_api_key(allow_user_permission=True)
    def get(self, uid):
        ban = Ban.objects(uid=uid).first()
        if ban is None:
            abort(404)

        user = request.api_user._get_current_object()

        return {
            'uid': uid,
            'watching': user in ban.watching
        }

    put_parser = RequestParser()
    put_parser.add_argument("watch", type=str, required=True)

    @require_api_key(required_access_tokens=['anathema.bans.watch'], allow_user_permission=True)
    def put(self, uid):
        args = self.put_parser.parse_args()
        watch = args.get("watch").lower() == "true"

        ban = Ban.objects(uid=uid).first()
        if ban is None:
            abort(404)

        user = request.api_user._get_current_object()

        if user in ban.watching:
            if not watch:
                ban.watching.remove(user)
        else:
            if watch:
                ban.watching.append(user)
        ban.save()

        return {
            'uid': uid,
            'watching': user in ban.watching
        }


rest_api.add_resource(Bans, '/anathema/bans')
rest_api.add_resource(WatchBan, '/anathema/ban/<int:uid>/watch')

register_api_access_token('anathema.bans.get')
register_api_access_token('anathema.bans.post', permission="api.anathema.bans.post")
register_api_access_token('anathema.bans.delete', permission="api.anathema.bans.delete")

register_api_access_token('anathema.bans.watch', permission=permissions.ban_watch)
