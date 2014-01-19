__author__ = 'zifnab'

from flask_superadmin.contrib.mongoenginemodel import ModelAdmin
from flask_login import current_user

class BaseModel(ModelAdmin):
    permission='admin'
    def is_accessible(self):
        return current_user.has_permission(self.permission)

class ForumModel(BaseModel):
    permission='admin.database.forum'

class AuthModel(BaseModel):
    permission='admin.database.auth'

class BanModel(BaseModel):
    permission='admin.database.bans'

class AltModel(BaseModel):
    permission='admin.database.alts'