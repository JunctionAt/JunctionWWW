from flask import request
from flask.ext.restful import Resource

from blueprints.api import require_api_key
from blueprints.base import rest_api

add_api_username_verification_token = 'api.auth.add_ip_username_verification'


class MeResource(Resource):

    @require_api_key(asuser_must_be_registered=False,
                     allow_user_permission=True)
    def get(self):
        user = getattr(request, 'api_user', None)
        username = getattr(request, 'api_user_name', None)
        player = getattr(request, 'api_player', None)

        if player is not None:
            player_info = {
                'uuid': player.uuid,
                'mcname': player.mcname
            }
        else:
            player_info = None

        if user is not None:
            user_info = {
                'name': user.name
            }
        else:
            user_info = None

        return {'api_user_method': getattr(request, 'api_user_method'),
                'name_provided': username,
                'user': user_info,
                'player': player_info}


rest_api.add_resource(MeResource, '/auth/me')