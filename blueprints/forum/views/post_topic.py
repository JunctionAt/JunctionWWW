from flask import render_template, request, redirect, abort
from flask_wtf import Form
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import InputRequired, Length

from .. import blueprint
from blueprints.auth import login_required, current_user
from models.forum_model import Board, Topic, TopicEdit, Post, PostEdit


class PostTopicForm(Form):
    title = StringField("Title", validators=[
        InputRequired(message="A title is required."),
        Length(min=3, max=80, message="A title must be between 3 and 30 characters.")])
    content = TextAreaField("Content", validators=[
        InputRequired(message="Some content is required."),
        Length(min=1, max=5000, message="Content must be between 1 and 5000 characters long.")])
    submit = SubmitField("Submit")


@blueprint.route('/forum/b/<int:board_id>/<string:board_name>/post/', methods=['GET', 'POST'])
@login_required
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
        topic.date = post.date
        topic.save()

        return redirect(topic.get_url())
