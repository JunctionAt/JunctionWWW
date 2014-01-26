__author__ = 'HansiHE'

from flask_wtf import Form
from flask.ext.admin.contrib import mongoengine as mongoview
from flask.ext import admin
from blueprints.auth.user_model import User
from flask_login import current_user

def can(user, feature):
    if user.has_permission('admin.%s' % feature):
        return True
    return False

class AdminIndexView(admin.AdminIndexView):
    def is_accessible(self):
        return can(current_user, 'index')

class ModelView(mongoview.ModelView):
    form_base_class = Form
    def is_accessible(self):
        return can(current_user, 'mongo.%s' % self.model.__class__.__name__)
