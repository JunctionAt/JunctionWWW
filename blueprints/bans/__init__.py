from flask import Blueprint
from ban_model import Ban, Note

bans = Blueprint('bans', __name__, template_folder="templates")

import views.api
import views.note_indexes
import views.ban_indexes
import views.appeal_indexes
import views.appeal_post
import views.appeal_manage
import views.appeal_edit
import views.general
