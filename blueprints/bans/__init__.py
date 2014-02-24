from flask import Blueprint
from ban_model import Ban, Note
from datetime import datetime

bans = Blueprint('bans', __name__, template_folder="templates")

#import views.api
import views.ban_indexes
import views.ban_unified_view
import views.general
import api
