from flask import Blueprint

bans = Blueprint('bans', __name__, template_folder="templates")

#import views.api
import views.ban_indexes
import views.ban_unified_view
import views.ban_editing
import views.ban_manage
import views.general
import api
