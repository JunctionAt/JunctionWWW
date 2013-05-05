from flask import Blueprint, render_template, url_for
import os
import time

import base36_filter

blueprint = Blueprint('forum', __name__, template_folder='templates')

#@blueprint.route("/forum/servertime")
#def time_at_server():
#    return time.asctime()

#@blueprint.route("/forum/")
#def index():
#    return render_template("index.html")

import database.forum

import views.forum_views
import views.board_views
import views.post_topic
import views.topic_view
import views.post_reply