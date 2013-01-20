__author__ = 'HansiHE'

from flask import Blueprint, request, render_template, abort, send_file, flash, redirect, url_for, current_app
from blueprints.auth import login_required
from blueprints.admin.view import ModelView
from blueprints.base import admin

from blueprints.auth.user_model import Role_Group, User

admin.add_view(ModelView(Role_Group))
admin.add_view(ModelView(User))