__author__ = 'HansiHE'

from .. import blueprint
from flask import render_template, request, redirect, url_for, abort
from blueprints.auth import login_required, current_user
from ..database.forum import Forum, Category, Board, Topic, TopicEdit, Post, PostEdit
from wtforms import Form, TextField, TextAreaField, SubmitField
from wtforms.validators import Required, Length

@blueprint.route('/forum/t/<int:topic_id>/<string:topic_name>/', defaults={'page': 1})
@blueprint.route('/forum/t/<int:topic_id>/<string:topic_name>/page/<int:page>/')
def view_topic(topic_id, topic_name, page):
    topic = Topic.objects(topic_url_id=topic_id).first()
    if topic is None:
        abort(404)
    if not topic_name == topic.get_url_name():
        return redirect(topic.get_url())

    board = topic.board
    forum = board.forum
    posts = Post.objects(topic=topic).order_by('-date')

    for post in posts:
        print post.date

    return render_template('forum_topic_view.html', topic=topic, board=board, forum=forum, posts=posts)