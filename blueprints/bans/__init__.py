from flask import Blueprint
from ban_model import Ban, Note
from datetime import datetime

bans = Blueprint('bans', __name__, template_folder="templates")

def process_ban(ban):
    if not ban.active:
        return False
    if ban.removed_time is not None and ban.removed_time < datetime.utcnow():
        ban.active = False
        ban.save()
        return False
    return True

import views.api
import views.note_indexes
import views.ban_indexes
import views.appeal_indexes
import views.appeal_post
import views.appeal_manage
import views.appeal_edit
import views.general