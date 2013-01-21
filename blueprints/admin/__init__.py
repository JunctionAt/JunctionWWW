__author__ = 'HansiHE'

from flask import Blueprint, request, render_template, abort, send_file, flash, redirect, url_for, current_app
from blueprints.auth import login_required
from blueprints.admin.view import ModelView
from blueprints.base import admin
from flask.ext.admin.model import typefmt
import mongoengine

from blueprints.auth.user_model import Role_Group, User

#The Role Groups collection view
class Role_Group_View(ModelView):
    column_searchable_list = ['name']

admin.add_view(Role_Group_View(Role_Group, endpoint='mongo_role_groups', category='Mongo'))

#The Users collection view
class User_View(ModelView):
    column_filters = ['api_account']
    column_searchable_list = ['name', 'mail']
    form_excluded_columns = ['notifications']
    column_exclude_list = ['notifications', 'hash']

admin.add_view(User_View(User, endpoint='mongo_user', category='Mongo'))