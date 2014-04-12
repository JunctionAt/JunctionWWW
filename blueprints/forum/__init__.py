from flask import Blueprint

blueprint = Blueprint('forum', __name__, template_folder='templates')

from views import board_views, forum_views, post_reply, post_topic, topic_edit, topic_view, post_permalink
