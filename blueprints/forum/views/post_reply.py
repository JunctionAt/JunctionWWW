__author__ = 'HansiHE'

from .. import blueprint
from blueprints.auth import current_user, login_required
from flask import render_template, request, redirect, url_for, abort
from ..database.forum import Forum, Category, Board, Topic, Post, PostEdit
from wtforms import Form, TextAreaField, SubmitField
from wtforms.validators import Required, Length


class TopicReplyForm(Form):
    content = TextAreaField("Content", validators=[
        Required(message="Some content is required."),
        Length(min=1, max=5000, message="Content must be between 1 and 5000 characters long.")])
    submit = SubmitField("Submit")


@login_required
@blueprint.route('/forum/t/<int:topic_id>/<string:topic_name>/post/', methods=['GET', 'POST'])
def post_reply(topic_id, topic_name):
    topic = Topic.objects(topic_url_id=topic_id).first()
    if topic is None:
        abort(404)
    if not topic_name == topic.get_url_name():
        return redirect(topic.get_url())
    board = topic.board
    forum = board.forum

    form = TopicReplyForm(request.form)

    if request.method == 'GET':
        return render_template('forum_post_reply.html', forum=forum, board=board, topic=topic, form=form)

    elif request.method == 'POST':
        if not form.validate():
            return render_template('forum_post_reply.html', forum=forum, board=board, topic=topic, form=form)

        post = Post(author=current_user.to_dbref(), content=form.content.data, topic=topic,
                    forum=forum)
        post_edit = PostEdit(author=post.author, content=post.content, date=post.date)
        post.edits.append(post_edit)
        post.save()

        return redirect(topic.get_url())