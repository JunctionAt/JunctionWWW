from flask.ext.superadmin import ModelAdmin

from blueprints.base import admin
from blueprints.auth import current_user
from models.user_model import Role_Group, User
from models.forum_model import Forum, Category, Board, Topic, Post
from models.ban_model import Ban, AppealReply, Note
from models.alts_model import IpPlayersModel, PlayerIpsModel
from models.servers_model import Server


def permission_model(permission):
    class AuthModel(ModelAdmin):
        def is_accessible(self):
            return current_user.has_permission('admin.%s' % permission)
    return AuthModel


# Users
admin.register(Role_Group, permission_model('role_group'), name='Role Groups', category='Users', endpoint='admin_role_groups')

class UserModel(permission_model('user')):
    search_fields = ['name', 'mail']
    fields = ['name', 'registered', 'hash', 'roles', 'role_groups', 'mail', 'mail_verified']
    readonly_fields = ['registered']
    can_create = False
    can_delete = False
admin.register(User, UserModel, category='Users', endpoint='admin_users')


# Forum
admin.register(Forum, permission_model('forum_forum'), category='Forum', endpoint='admin_forum_forum')
admin.register(Category, permission_model('forum_category'), category='Forum', endpoint='admin_forum_category')
admin.register(Board, permission_model('forum_board'), category='Forum', endpoint='admin_forum_board')
admin.register(Topic, permission_model('forum_topic'), category='Forum', endpoint='admin_forum_topic')
admin.register(Post, permission_model('forum_post'), category='Forum', endpoint='admin_forum_post')


# Anathema
class BanModel(permission_model('ban')):
    fields = ['uid', 'issuer', 'username', 'reason', 'server', 'time', 'active']
    readonly_fields = ['uid', 'issuer', 'username', 'reason', 'server', 'time', 'active']
    exclude = ['state']
    can_delete = False
    can_create = False
admin.register(Ban, BanModel, category='Anathema', endpoint='admin_ban')
admin.register(Note, permission_model('note'), category='Anathema', endpoint='admin_note')
admin.register(AppealReply, permission_model('appeal_reply'), category='Anathema', endpoint='admin_appeal_reply')

# Alts
class IpPlayersAdminModel(permission_model('alts')):
    can_edit = False
    can_create = False
    can_delete = False
admin.register(IpPlayersModel, IpPlayersAdminModel, category='Alts', endpoint='admin_ip_players')

class PlayerIpsAdminModel(permission_model('alts')):
    can_edit = False
    can_create = False
    can_delete = False
admin.register(PlayerIpsModel, PlayerIpsAdminModel, category='Alts', endpoint='admin_player_ips')

# Servers
class ServerModel(permission_model('servers')):
    readonly_fields = []
admin.register(Server, ServerModel, name='Servers', endpoint='admin_servers')