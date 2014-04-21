from blueprints.uuid_utils import NoSuchUserException

__author__ = 'hansihe'

from blueprints.api import require_api_key, register_api_access_token
from models.player_model import MinecraftPlayer
from blueprints.base import rest_api
from blueprints import uuid_utils

from flask.ext.restful import Resource
from flask.ext.restful.reqparse import RequestParser


class UUIDApi(Resource):

    get_parser = RequestParser()
    get_parser.add_argument("uuid", type=uuid_utils.uuid_type)
    get_parser.add_argument("name", type=str)

    def validate_get(self, args):
        if not args.get("uuid") and not args.get("name"):
            return {'error': [{"message": "you must either query for a uuid or a name"}]}

    @require_api_key(required_access_tokens=['uuid.get'], allow_user_permission=True)
    def get(self):
        args = self.get_parser.parse_args()
        validate_args = self.validate_get(args)
        if validate_args:
            return validate_args

        uuid = args.get("uuid")
        mcname = args.get("name")

        if uuid:
            try:
                player = MinecraftPlayer.find_or_create_player(uuid)
            except NoSuchUserException, e:
                return {'error': [{"message": e.message}]}
            return {'uuid': player.uuid, 'name': player.mcname}

        if mcname:
            try:
                uuid, mcname = uuid_utils.lookup_uuid_name(mcname)
            except NoSuchUserException, e:
                return {'error': [{"message": e.message}]}
            player = MinecraftPlayer.find_or_create_player(uuid, mcname)
            return {'uuid': player.uuid, 'name': player.mcname}


rest_api.add_resource(UUIDApi, '/uuid')

register_api_access_token('uuid.get', permission='api.uuid.get')
