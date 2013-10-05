__author__ = 'hansihe'

from blueprints.api import require_api_key, register_api_access_token
from flask.ext.restful import Resource
from ..user_model import User
from blueprints.base import rest_api
from mongoengine import Q


class GroupList(Resource):

    #@require_api_key(['auth.groups.list.get'])
    def get(self):
        users = User.objects(Q(role_groups__exists=True) & Q(role_groups__not__size=0)).scalar('name', 'role_groups')

        user_groups = dict()
        for name, groups in users:
            user_groups[name] = dict(groups=groups)

        return {'users': user_groups}

rest_api.add_resource(GroupList, '/auth/groups/list')
register_api_access_token('auth.groups.list.get')
