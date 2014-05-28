from flask import abort, redirect

from .. import blueprint
from models.forum_model import Post


@blueprint.route('/forum/p/<string:post_id>', defaults={'dummy_name': ""})
@blueprint.route('/forum/p/<string:post_id>/<string:dummy_name>')
def permalink_post_redirect(post_id, dummy_name):

    post = Post.objects(id=post_id).first()
    if post is None:
        abort(404)

    return redirect(post.get_post_url())