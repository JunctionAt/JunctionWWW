__author__ = 'HansiHE'

from flask import Blueprint
from flask.ext.restful import Resource
import ipaddress
import re
from flask.ext.restful.reqparse import RequestParser

from models.alts_model import PlayerIpsModel, IpPlayersModel
from blueprints.api import require_api_key, register_api_access_token, datetime_format
from blueprints.base import rest_api
from blueprints import uuid_utils
from models.player_model import MinecraftPlayer


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
    get_parser.add_argument("uuid", type=uuid_utils.uuid_type, required=True)

    @require_api_key(required_access_tokens=['anathema.alts.get'], allow_user_permission=True)
    def get(self):
        args = self.get_parser.parse_args()
        uuid = args.get("uuid")

        alts = []
        user_ips = PlayerIpsModel.objects(player=uuid).first()
        if user_ips:
            alt_objects = PlayerIpsModel.objects(ips__in=user_ips.ips, player__ne=uuid)
            for alt_object in alt_objects:
                alts.append({"player": {"name": alt_object.player.mcname, "uuid": alt_object.player.uuid}, "last_login": alt_object.last_login.strftime(datetime_format)})
        return {'alts': alts}

    post_parser = RequestParser()
    post_parser.add_argument("uuid", type=uuid_utils.uuid_type, required=True)
    post_parser.add_argument("ip", type=str, required=True, help="ip cannot be blank")

    @require_api_key(required_access_tokens=['anathema.alts.post'])
    def post(self):
        args = self.post_parser.parse_args()
        uuid = args.get("uuid")
        player = MinecraftPlayer.find_or_create_player(uuid)

        if not verify_ip_address(args["ip"].decode("ascii")):
            return {'error': [{"message": "ip is not valid"}]}
        ip = args["ip"]

        player_ips = PlayerIpsModel.objects(player=player).first()
        if not player_ips:
            player_ips = PlayerIpsModel(player=player, ips=[ip])
            player_ips.save()
        player_ips.update_last_login_and_add_entry(ip)

        ip_players = IpPlayersModel.objects(ip=ip).first()
        if not ip_players:
            ip_players = IpPlayersModel(ip=ip, players=[player])
            ip_players.save()
        ip_players.update_last_login_and_add_entry(player)

        return {"success": True}


rest_api.add_resource(Alts, '/anathema/alts')

register_api_access_token('anathema.alts.get', permission="api.anathema.alts.get")
register_api_access_token('anathema.alts.post', permission="api.anathema.alts.post")
