__author__ = 'HansiHE'

from flask import render_template, redirect, abort

from .. import blueprint
from ..database.forum import Topic, Post
from topic_edit import PostEditForm


@blueprint.route('/forum/t/<int:topic_id>/<string:topic_name>/', defaults={'page': 1})
@blueprint.route('/forum/t/<int:topic_id>/<string:topic_name>/page/<int:page>/')
def view_topic(topic_id, topic_name, page):

    post_edit_form = PostEditForm()

    topic = Topic.objects(topic_url_id=topic_id).first()
    if topic is None:
        abort(404)
    if not topic_name == topic.get_url_name():
        return redirect(topic.get_url())

    board = topic.board
    forum = board.forum
    posts = Post.objects(topic=topic).order_by('+date')

    for post in posts:
        print post.date

    return render_template('forum_topic_view.html', topic=topic, board=board, forum=forum, posts=posts, post_edit_form=post_edit_form)