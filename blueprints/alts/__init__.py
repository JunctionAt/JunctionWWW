__author__ = 'HansiHE'

from flask import Blueprint, request, render_template, abort, send_file, flash, redirect, url_for
from blueprints.auth import login_required
from alts_model import PlayerIpsModel, IpPlayersModel
from flask.ext.restful import Resource
from blueprints.api import require_api_key, register_api_access_token, datetime_format
import ipaddress
import re
from flask.ext.restful.reqparse import RequestParser
from blueprints.base import rest_api

alts = admin = Blueprint('alts', __name__, template_folder='templates')


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
    get_parser.add_argument("username", type=str, required=True, help="username cannot be blank")
    get_parser.add_argument("ip", type=str, required=True, help="ip cannot be blank")

    @require_api_key(access_tokens=['anathema.alts.update'])
    def post(self):
        args = self.get_parser.parse_args()

        if not validate_username(args["username"]):
            return {'error': [{"message": "username is not valid"}]}
        username = args["username"]

        if not verify_ip_address(args["ip"].decode("ascii")):
            return {'error': [{"message": "ip is not valid"}]}
        ip = args["ip"]

        player_ips = PlayerIpsModel.objects(username=username).first()
        if not player_ips:
            player_ips = PlayerIpsModel(username=username, ips=[ip])
        player_ips.update_last_login()
        player_ips.save()

        ip_players = IpPlayersModel.objects(ip=ip).first()
        if not ip_players:
            ip_players = IpPlayersModel(ip=ip, usernames=[username])
        ip_players.update_last_login()
        ip_players.save()

        return {"success": True}


rest_api.add_resource(Alts, '/anathema/alts')
register_api_access_token('anathema.alts.update', permission="api.anathema.alts.update")