from flask.ext.restful import Resource
from mongoengine import Q

from blueprints.api import register_api_access_token
from models.user_model import User
from blueprints.base import rest_api


class GroupList(Resource):

    #@require_api_key(['auth.groups.list.get'])
    def get(self):
        users = User.objects(Q(role_groups__exists=True) & Q(role_groups__not__size=0)).scalar('name', 'role_groups')

        user_groups = dict()
        for name, groups in users:
            user_groups[name] = dict(groups=map(lambda group: group.name, groups))

        return {'users': user_groups}

rest_api.add_resource(GroupList, '/auth/group/list')
register_api_access_token('auth.group.list.get')
