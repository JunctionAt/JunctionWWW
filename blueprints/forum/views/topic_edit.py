__author__ = 'HansiHE'

from .. import blueprint


@blueprint.route('/forum/e/<int:post_id>/')
def edit_post():
    pass