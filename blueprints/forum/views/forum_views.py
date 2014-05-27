__author__ = 'HansiHE'

from flask import render_template, redirect, url_for, abort, current_app

from blueprints.auth import current_user
from .. import blueprint
from models.forum_model import Forum, Category, Topic
from ..forum_util import forum_template_data


@blueprint.route('/forum/')
def forum_landing():
    return redirect(url_for('forum.view_forum', forum=current_app.config.get('DEFAULT_FORUM')))


@blueprint.route('/forum/f/<string:forum>/')
def view_forum(forum):
    forum = Forum.objects(identifier=forum).first()
    if forum is None:
        abort(404)
    categories = Category.objects(forum=forum)
    recent_topics = Topic.objects(forum=forum).order_by('-last_post_date').limit(10)

    if current_user.is_authenticated():
        read_topics = recent_topics.filter(users_read_topic__in=[current_user.id]).scalar('id')
    else:
        read_topics = None

    return render_template("forum_topics_display.html", categories=categories, forum=forum, topics=recent_topics,
                           read_topics=read_topics, forum_menu_current='latest', **forum_template_data(forum))

#@blueprint.route('/f/a/s/')
#def setup():
#    category = Category.objects.first()
#    forum = Forum.objects(identifier="main").first()
#    board = Board()
#    board.name = "General Chat"
#    board.forum = forum
#    board.categories = [category]
#    board.description = "Put chatter here pls"
#    board.save()
#    return 'yes'