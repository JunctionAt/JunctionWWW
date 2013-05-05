__author__ = 'HansiHE'

from .. import blueprint
from flask import render_template, request, redirect, url_for, abort
from blueprints.auth import login_required, current_user
from ..database.forum import Forum, Category, Board, Topic, TopicEdit, Post, PostEdit
from wtforms import Form, TextField, TextAreaField, SubmitField
from wtforms.validators import Required, Length


class PostTopicForm(Form):
    title = TextField("Title", validators=[
        Required(message="A title is required."),
        Length(min=3, max=30, message="A title must be between 3 and 30 characters.")])
    content = TextAreaField("Content", validators=[
        Required(message="Some content is required."),
        Length(min=1, max=5000, message="Content must be between 1 and 5000 characters long.")])
    submit = SubmitField("Submit")


@login_required
@blueprint.route('/forum/b/<int:board_id>/<string:board_name>/post/', methods=['GET', 'POST'])
def post_topic(board_id, board_name):
    board = Board.objects(board_id=board_id).first()
    if board is None:
        abort(404)
    forum = board.forum

    form = PostTopicForm(request.form)

    if request.method == 'GET':
        return render_template('forum_post_topic.html', board=board, forum=forum, form=form)

    elif request.method == 'POST':
        if not form.validate():
            return render_template('forum_post_topic.html', board=board, forum=forum, form=form)

        topic = Topic(title=form.title.data, author=current_user.to_dbref(), forum=forum, board=board)
        topic_edit = TopicEdit(title=topic.title, date=topic.date,
                               announcement=topic.announcement, author=topic.author)
        topic.edits.append(topic_edit)
        topic.save()

        post = Post(author=current_user.to_dbref(), content=form.content.data, topic=topic,
                    forum=forum, date=topic.date, is_op=True)
        post_edit = PostEdit(author=post.author, content=post.content, date=post.date)
        post.edits.append(post_edit)
        post.save()

        topic.op = post
        topic.save()

        return redirect(topic.get_url())