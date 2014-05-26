__author__ = 'HansiHE'

from flask import abort, render_template, request, redirect
from flask_wtf import Form
from wtforms import TextAreaField, SubmitField
from wtforms.validators import InputRequired, Length
from datetime import datetime
from bson.objectid import ObjectId

from .. import blueprint
from models.forum_model import Post, PostEdit
from blueprints.auth import current_user
from blueprints.auth import login_required


class PostEditForm(Form):
    content = TextAreaField("Content", validators=[
        InputRequired(message="Some content is required."),
        Length(min=1, max=5000, message="Content must be between 1 and 5000 characters long.")])
    submit = SubmitField("Submit")


@blueprint.route('/forum/e/<string:post_id>/', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    form = PostEditForm(request.form)

    if not ObjectId.is_valid(post_id):
        abort(404)

    post = Post.objects(id=post_id).first()
    if post is None:
        abort(404)

    if not post.can_edit(current_user):
        abort(403)

    topic = post.topic
    board = topic.board
    forum = post.forum

    if request.method == 'POST' and form.validate():
        post_edit = PostEdit(author=current_user.to_dbref(), content=form.content.data, date=datetime.utcnow())
        post.edits.append(post_edit)
        post.content = form.content.data
        post.save()

        return redirect(topic.get_url())

    form.content.data = post.content
    return render_template('forum_post_edit.html', form=form, topic=topic, board=board, forum=forum)
