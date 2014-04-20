from blueprints import uuid_utils
from models.player_model import MinecraftPlayer

__author__ = 'HansiHE'

from flask import Blueprint
from flask.ext.restful import Resource
import ipaddress
import re
from flask.ext.restful.reqparse import RequestParser

from models.alts_model import PlayerIpsModel, IpPlayersModel
from blueprints.api import require_api_key, register_api_access_token
from blueprints.base import rest_api


alts = Blueprint('alts', __name__, template_folder='templates')


import views.graph_lookup_view


def validate_username(username):
    if 2 <= len(username) <= 16 and re.match(r'^[A-Za-z0-9_]+$', username):
        return True
    return False


def verify_ip_address(addr):
    try:
        print ipaddress.ip_address(addr)
        return True
    except ValueError:
        return False


class Alts(Resource):

    get_parser = RequestParser()
    get_parser.add_argument("username", type=str, required=True, help="a username must be provided") # TODO: Remove when our shit is updated
    get_parser.add_argument("uuid", type=str)

    @require_api_key(required_access_tokens=['anathema.alts.get'], allow_user_permission=True)
    def get(self):
        args = self.get_parser.parse_args()

        if not validate_username(args["username"]):
            return {'error': [{"message": "username is not valid"}]}
        username = args["username"]
        uuid = args.get("uuid") or uuid_utils.lookup_uuid(username)
        if uuid is None:
            return {'error': [{"message": "uuid cannot be looked up from username"}]}

        alts = []
        user_ips = PlayerIpsModel.objects(player=uuid).first()
        if user_ips:
            alt_objects = PlayerIpsModel.objects(ips__in=user_ips.ips, player__not=uuid)
            for alt_object in alt_objects:
                alts.append({"alt": alt_object.username, "uuid": alt_object.player.uuid, "last_login": str(alt_object.last_login)})
        return {'alts': alts}

    post_parser = RequestParser()
    post_parser.add_argument("username", type=str, required=True, help="username cannot be blank")
    post_parser.add_argument("uuid", type=str)  # TODO: Make required when our shit is updated
    post_parser.add_argument("ip", type=str, required=True, help="ip cannot be blank")

    @require_api_key(required_access_tokens=['anathema.alts.post'])
    def post(self):
        args = self.post_parser.parse_args()

        if not validate_username(args["username"]):
            return {'error': [{"message": "username is not valid"}]}
        username = args["username"]
        uuid = args.get("uuid") or uuid_utils.lookup_uuid(username)
        if uuid is None:
            return {'error': [{"message": "uuid cannot be looked up from username"}]}
        
        player = MinecraftPlayer.find_or_create_player(uuid, username)

        if not verify_ip_address(args["ip"].decode("ascii")):
            return {'error': [{"message": "ip is not valid"}]}
        ip = args["ip"]

        player_ips = PlayerIpsModel.objects(player=player).first()
        if not player_ips:
            player_ips = PlayerIpsModel(username=username, player=player, ips=[ip])
            player_ips.save()
        player_ips.update_last_login_and_add_entry(ip)

        ip_players = IpPlayersModel.objects(ip=ip).first()
        if not ip_players:
            ip_players = IpPlayersModel(ip=ip, usernames=[username], players=[player])
            ip_players.save()
        ip_players.update_last_login_and_add_entry(player)

        return {"success": True}


rest_api.add_resource(Alts, '/anathema/alts')

register_api_access_token('anathema.alts.get', permission="api.anathema.alts.get")
register_api_access_token('anathema.alts.post', permission="api.anathema.alts.post")
