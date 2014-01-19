__author__ = 'zifnab'

from flask_superadmin import BaseView, expose
from flask_login import current_user

from blueprints.bans.ban_model import Ban, Note

class PermissionView(BaseView):
    permission='admin'
    def is_accessible(self):
        return current_user.has_permission(self.permission)

class IndexView(PermissionView):
    permission='admin.index'
    @expose('/')
    def index(self):
        return self.render('index.html')

class BanLookupView(PermissionView):
    permission='admin.lookup.ban'
    @expose('/')
    def index(self):
        return self.render('admin/layout.html', name='Junction Administration')

class NoteLookupView(PermissionView):
    permission='admin.lookup.note'
    @expose('/')
    def index(self):
        return self.render('admin/layout.html')

class AltLookupView(PermissionView):
    permission='admin.lookup.alt'
    @expose('/')
    def index(self):
        return self.render('admin/layout.html')