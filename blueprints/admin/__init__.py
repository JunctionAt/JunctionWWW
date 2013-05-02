__author__ = 'HansiHE'

from flask import Blueprint, request, render_template, abort, send_file, flash, redirect, url_for, current_app
from blueprints.auth import login_required
from blueprints.admin.view import ModelView
from blueprints.base import admin
from blueprints.forum.database.forum import Forum, Category, Board
from flask.ext.admin.model import typefmt
import mongoengine

from blueprints.auth.user_model import Role_Group, User

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

admin.add_view(Forum_Forum_View(Forum, endpoint='forum_forum', category='Mongo Forum'))

#Forum categories
class Forum_Category_View(ModelView):
    pass

admin.add_view(Forum_Category_View(Category, endpoint='forum_categories', category='Mongo Forum'))

#Forum boards
class Forum_Board_View(ModelView):
    pass

admin.add_view(Forum_Board_View(Board, endpoint='forum_boards', category='Mongo Forum'))