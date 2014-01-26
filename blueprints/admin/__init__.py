__author__ = 'HansiHE'

from flask import Blueprint, request, render_template, abort, send_file, flash, redirect, url_for, current_app
from blueprints.auth import login_required
from blueprints.admin.view import ModelView
from blueprints.base import admin
from blueprints.forum.database.forum import Forum, Category, Board, Topic, Post
from flask.ext.admin.model import typefmt
from blueprints.bans.ban_model import Ban, AppealReply, Note
from blueprints.alts.alts_model import PlayerIpsModel, IpPlayersModel
import mongoengine

from blueprints.auth.user_model import Role_Group, User
from blueprints.alts.alts_model import IpPlayersModel, PlayerIpsModel

#The Role Groups collection view
class Role_Group_View(ModelView):
    column_searchable_list = ['name']

admin.add_view(Role_Group_View(Role_Group, endpoint='mongo_role_groups', category='Mongo General'))


#The Users collection view
class User_View(ModelView):
    column_filters = ['api_account']
    column_searchable_list = ['name', 'mail']
    form_excluded_columns = ['notifications']
    column_exclude_list = ['notifications', 'hash']
    column_descriptions = {'roles': "This shouldn't be used normally."}

admin.add_view(User_View(User, endpoint='mongo_user', category='Mongo General'))


#The forums view
class Forum_Forum_View(ModelView):
    pass

admin.add_view(Forum_Forum_View(Forum, endpoint='admin_forum_forum', category='Mongo Forum'))

#Forum categories
class Forum_Category_View(ModelView):
    pass

admin.add_view(Forum_Category_View(Category, endpoint='admin_forum_categories', category='Mongo Forum'))


#Forum boards
class Forum_Board_View(ModelView):
    pass

admin.add_view(Forum_Board_View(Board, endpoint='admin_forum_boards', category='Mongo Forum'))


class Forum_Topic_View(ModelView):
    pass

admin.add_view(Forum_Topic_View(Topic, endpoint='admin_forum_topics', category='Mongo Forum'))


class Forum_Post_View(ModelView):
    pass

admin.add_view(Forum_Post_View(Post, endpoint='admin_forum_posts', category='Mongo Forum'))


#Bans
class Ban_View(ModelView):
    action_disallowed_list = ['delete']
    column_exclude_list = ['appeal']
    form_excluded_columns = ['time', 'removed_time', 'removed_by', 'active']
    column_searchable_list = ['username', 'reason', 'server', 'issuer']
admin.add_view(Ban_View(Ban, endpoint='admin_bans', category='Anathema'))

#Notes
class Notes_View(ModelView):
    pass
admin.add_view(Notes_View(Note, endpoint='admin_notes', category='Anathema'))

class AppealReply_View(ModelView):
    pass

admin.add_view(AppealReply_View(AppealReply, endpoint='admin_appealreplies', category='Anathema'))

#Alt Lookup
class IpPlayer_View(ModelView):
    can_delete = False
    can_edit = False
    can_create = False
    column_searchable_list = ['ip']
    column_filters = ['last_login']
admin.add_view(IpPlayer_View(IpPlayersModel, endpoint='admin_alt_ip', category='Mongo Alts'))

class PlayerIp_View(ModelView):
    can_delete = False
    can_edit = False
    can_create = False
    column_searchable_list = ['username']
    column_filters = ['last_login']
admin.add_view(PlayerIp_View(PlayerIpsModel, endpoint='admin_alt_username', category='Mongo Alts'))
