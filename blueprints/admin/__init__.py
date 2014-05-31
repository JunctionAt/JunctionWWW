from flask_superadmin import ModelAdmin

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
class RoleGroupModel(permission_model('role_group')):
    list_display = ['name']
admin.register(Role_Group, RoleGroupModel, name='Role Groups', category='Users', endpoint='admin_role_groups')


class UserModel(permission_model('user')):
    list_display = ['name', 'mail']
    search_fields = ['name', 'mail']
    fields = ['name', 'registered', 'hash', 'roles', 'role_groups', 'mail', 'mail_verified', 'tfa', 'tfa_method', 'tfa_secret', 'tfa_info']
    readonly_fields = ['registered', 'tfa_info']
    can_create = False
    can_delete = False
admin.register(User, UserModel, category='Users', endpoint='admin_users')


# Forum
class ForumModel(permission_model('forum_forum')):
    list_display = ['name', 'identifier']
admin.register(Forum, ForumModel, category='Forum', endpoint='admin_forum_forum')


class CategoryModel(permission_model('forum_category')):
    list_display = ['name', 'forum']
admin.register(Category, CategoryModel, category='Forum', endpoint='admin_forum_category')


class BoardModel(permission_model('forum_board')):
    list_display = ['name', 'forum']
admin.register(Board, BoardModel, category='Forum', endpoint='admin_forum_board')


class TopicModel(permission_model('forum_topic')):
    list_display = ['title', 'author', 'last_editor', 'date', 'board', 'forum']
admin.register(Topic, TopicModel, category='Forum', endpoint='admin_forum_topic')


class PostModel(permission_model('forum_post')):
    list_display = ['author', 'topic', 'date', 'forum']
admin.register(Post, PostModel, category='Forum', endpoint='admin_forum_post')


# Anathema
class BanModel(permission_model('ban')):
    list_display = ['uid', 'username', 'issuer', 'reason', 'server', 'time', 'active']
    fields = ['uid', 'issuer', 'username', 'reason', 'server', 'time', 'active']
    readonly_fields = ['uid', 'issuer', 'username', 'reason', 'server', 'time', 'active']
    exclude = ['state']
    can_delete = False
    can_create = False
admin.register(Ban, BanModel, category='Anathema', endpoint='admin_ban')


class NoteModel(permission_model('note')):
    list_display = ['uid', 'username', 'issuer', 'note', 'server', 'time', 'active']
admin.register(Note, NoteModel, category='Anathema', endpoint='admin_note')


class AppealReplyModel(permission_model('appeal_reply')):
    list_display = ['creator', 'ban', 'created', 'editor', 'edited']
admin.register(AppealReply, AppealReplyModel, category='Anathema', endpoint='admin_appeal_reply')


# Alts
class IpPlayersAdminModel(permission_model('alts')):
    list_display = ['ip', 'players', 'last_login']
    search_fields = ['ip']
    can_edit = False
    can_create = False
    can_delete = False
admin.register(IpPlayersModel, IpPlayersAdminModel, name='IP -> Players', category='Alts', endpoint='admin_ip_players')


class PlayerIpsAdminModel(permission_model('alts')):
    list_display = ['player', 'ips', 'last_login']
    search_fields = ['player']
    can_edit = False
    can_create = False
    can_delete = False
admin.register(PlayerIpsModel, PlayerIpsAdminModel, name='Player -> IPs', category='Alts', endpoint='admin_player_ips')


# Servers
class ServerModel(permission_model('servers')):
    list_display = ['name', 'server_id']
admin.register(Server, ServerModel, name='Servers', endpoint='admin_servers')
