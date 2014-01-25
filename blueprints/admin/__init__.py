__author__ = 'zifnab'

from flask import current_app
from flask_superadmin import Admin
from blueprints.admin.models import AuthModel, ForumModel, BanModel, AltModel

import views

from blueprints.forum.database.forum import Forum, Category, Board, Topic, Post
from blueprints.bans.ban_model import Ban, Note, Appeal

from blueprints.alts.alts_model import PlayerIpsModel, IpPlayersModel
import mongoengine

from blueprints.auth.user_model import Role_Group, User
from blueprints.alts.alts_model import IpPlayersModel, PlayerIpsModel

admin = Admin(app=current_app, name='Admin - Junction')

#Important - https://github.com/SyrusAkbary/Flask-SuperAdmin/blob/master/flask_superadmin/model/base.py

#Auth
class Role_Group_Model(AuthModel):
    list_display=('name', 'roles')
    search_fields=('name', 'roles')

class User_Model(AuthModel):
    fields=('name', 'mail', 'reddit_username', 'registered', 'role_groups', 'roles', 'api_account')
    list_display=('name', 'mail', 'reddit_username', 'registered', 'role_groups', 'roles', 'api_account')
    search_fields=('name', 'mail', 'reddit_username', 'role_groups', 'roles')
    can_delete=False

#Forum
class Forum_Forum_Model(ForumModel):
    list_display=('name', 'identifier')
    search_fields=('name')

class Forum_Category_Model(ForumModel):
    list_display=('name', 'description', 'order', 'forum')
    search_fields=('name', 'description')

class Forum_Board_Model(ForumModel):
    list_display=('name', 'description')
    search_fields=('name', 'description')
    pass

class Forum_Topic_Model(ForumModel):
    list_display = ('title', 'author', 'date')
    search_fields=('title', 'author')

class Forum_Post_Model(ForumModel):
    list_display = ('author', 'content', 'date')
    search_fields=('author', 'content')

#Bans/Alts
class Ban_Model(BanModel):
    list_display = ('username', 'reason', 'issuer', 'time', 'server', 'active')
    search_fields = ('username', 'reason', 'issuer', 'server', 'active', 'removed_by')
    fields = ('username', 'issuer', 'server', 'active', 'removed_time', 'removed_by', 'appeal')

class Note_Model(BanModel):
    list_display = ('issuer', 'username', 'note', 'server', 'time', 'active')
    search_fields=('issuer', 'username', 'note', 'server', 'active')

class IP_Alt_Model(AltModel):
    list_display = ('username', 'ips')
    search_fields=('username', 'ips')

class Username_Alt_Model(AltModel):
    list_display = ('ip', 'usernames')
    search_fields = ('ip', 'usernames')

#Auth
admin.register(Role_Group, Role_Group_Model, category='Mongo.Auth')
admin.register(User, User_Model, category='Mongo.Auth')

#Forum
admin.register(Forum, Forum_Forum_Model, category='Mongo.Forum', endpoint='forum2')
admin.register(Category, Forum_Category_Model, category='Mongo.Forum')
admin.register(Board, Forum_Board_Model, category='Mongo.Forum')
admin.register(Topic, Forum_Topic_Model, category='Mongo.Forum')
admin.register(Post, Forum_Post_Model, category='Mongo.Forum')

#Bans/Notes/Alts
admin.register(Ban, Ban_Model, category='Mongo.Bans')
admin.register(Note, Note_Model, category='Mongo.Bans')
admin.register(PlayerIpsModel, IP_Alt_Model, category='Mongo.Alts')
admin.register(IpPlayersModel, Username_Alt_Model, category='Mongo.Alts')

#Custom Views
admin.add_view(views.BanLookupView(name='Bans', category='Lookup'))
admin.add_view(views.NoteLookupView(name='Notes', category='Lookup'))
admin.add_view(views.AltLookupView(name='Alts', category='Lookup'))
