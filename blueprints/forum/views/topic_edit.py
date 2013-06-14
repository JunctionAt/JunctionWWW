__author__ = 'HansiHE'

from .. import blueprint
from ..database.forum import Post, PostEdit
from flask import abort, render_template, request, redirect
from wtforms import Form, TextAreaField
from wtforms.validators import Required, Length
from blueprints.auth import current_user
from datetime import datetime
from bson.objectid import ObjectId
from blueprints.auth import login_required


class PostEditForm(Form):
    content = TextAreaField("Content", validators=[
        Required(message="Some content is required."),
        Length(min=1, max=5000, message="Content must be between 1 and 5000 characters long.")])


@login_required
@blueprint.route('/forum/e/<string:post_id>/', methods=['GET', 'POST'])
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