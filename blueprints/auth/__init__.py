from flask_login import LoginManager, AnonymousUserMixin
from flask import current_app, Blueprint

from permissions import PermissionHolderMixin

from models.user_model import User

login_manager = LoginManager()

login_manager.login_view = "auth.login"
login_manager.login_message = u"Please log in to access this page."
login_manager.login_message_category = "info"

login_manager.refresh_view = "auth.reauth"
login_manager.needs_refresh_message = u"To protect your account, please reauthenticate to access this page."
login_manager.needs_refresh_message_category = "info"

# Patch to keep other things importing these utilities from blueprints.auth working
from flask_login import current_user, login_required

@login_manager.user_loader
def user_loader(id):
    user = User.objects(name__iexact=id).first()
    return user


class Anon(AnonymousUserMixin, PermissionHolderMixin):
    def get_permissions(self):
        return []


login_manager.anonymous_user = Anon

login_manager.init_app(current_app, add_context_processor=True)
blueprint = Blueprint('auth', __name__, template_folder='templates')

from views import login, logout, reauth, setpassword, register, verify
from api import register, groups, uuid, me
