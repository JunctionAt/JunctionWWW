__author__ = 'HansiHE'

from flask import render_template, redirect, abort, url_for

from .. import blueprint
from ..database.forum import Topic, Post
from post_reply import TopicReplyForm
import math
from blueprints.auth import current_user

POSTS_PER_PAGE = 20
PAGINATION_VALUE_RANGE = 3


@blueprint.route('/forum/t/<int:topic_id>/<string:topic_name>/', defaults={'page': 1})
@blueprint.route('/forum/t/<int:topic_id>/<string:topic_name>/page/<int:page>/')
def view_topic(topic_id, topic_name, page):
    if page == 0:
        abort(404)

    topic_reply_form = TopicReplyForm()

    topic = Topic.objects(topic_url_id=topic_id).exclude().first()
    if topic is None:
        abort(404)
    if not topic_name == topic.get_url_name():
        return redirect(topic.get_url())

    if current_user.is_authenticated():
        topic.update(add_to_set__users_read_topic=current_user.to_dbref())

    board = topic.board
    forum = board.forum

    # Get our sorted posts and the number of posts.
    posts = Post.objects(topic=topic).order_by('+date')
    num_posts = len(posts)

    # Calculate the total number of pages and make sure the request is a valid page.
    num_pages = int(math.ceil(num_posts / float(POSTS_PER_PAGE)))
    if num_pages < page:
        if page == 1:
            return render_template('forum_topic_view.html', topic=topic, board=board, forum=forum,
                                   posts=posts, topic_reply_form=topic_reply_form,
                                   total_pages=num_pages, current_page=page, next=None, prev=None, links=[])
        abort(404)

    # Compile the list of topics we want displayed.
    display_posts = posts.skip((page - 1) * POSTS_PER_PAGE).limit(POSTS_PER_PAGE)

    # Find the links we want for the next/prev buttons if applicable.
    next_page = url_for('forum.view_topic', page=page + 1, **topic.get_url_info()) if page < num_pages \
        else None
    prev_page = url_for('forum.view_topic', page=page - 1, **topic.get_url_info()) if page > 1 and not num_pages == 1 \
        else None

    # Mash together a list of what pages we want linked to in the pagination bar.
    links = []
    for page_mod in range(-min(PAGINATION_VALUE_RANGE, page - 1), min(PAGINATION_VALUE_RANGE, num_pages-page) + 1):
        num = page + page_mod
        links.append({'num': num, 'url': url_for('forum.view_topic', page=num, **topic.get_url_info()),
                      'active': (num == page)})

    return render_template('forum_topic_view.html', topic=topic, board=board, forum=forum,
                           posts=display_posts, topic_reply_form=topic_reply_form,
                           total_pages=num_pages, current_page=page,
                           next=next_page, prev=prev_page, links=links)