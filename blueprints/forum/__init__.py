from flask import Blueprint

import base36_filter

blueprint = Blueprint('forum', __name__, template_folder='templates')

#@blueprint.route("/forum/servertime")
#def time_at_server():
#    return time.asctime()

#@blueprint.route("/forum/")
#def index():
#    return render_template("index.html")

import database.forum

from views import board_views, forum_views, post_reply, post_topic, topic_edit, topic_view