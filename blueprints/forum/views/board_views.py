__author__ = 'HansiHE'

import math

from flask import render_template, redirect, url_for, abort

from .. import blueprint
from ..database.forum import Board, Topic
from blueprints.auth import current_user


TOPICS_PER_PAGE = 10
PAGINATION_VALUE_RANGE = 3

@blueprint.route('/forum/b/<int:board_id>/')
def view_board_redirect(board_id):
    board = Board.objects(board_id=board_id).first()
    if board is None:
        abort(404)
    return redirect(url_for('forum.view_board', board_id=board_id, board_name=board.name.replace(' ', '_'), page=1))

@blueprint.route('/forum/b/<int:board_id>/<string:board_name>/', defaults={'page': 1})
@blueprint.route('/forum/b/<int:board_id>/<string:board_name>/page/<int:page>/')
def view_board(board_id, board_name, page):
    if page == 0:
        abort(404)

    board = Board.objects(board_id=board_id).first()
    if board is None:
        abort(404)
    if not board_name == board.get_url_name():
        return redirect(board.get_url())
    forum = board.forum

    # Get our sorted topics and the number of topics.
    topics = Topic.objects(board=board).order_by('-last_post_date')
    topic_num = len(topics)

    # Calculate the total number of pages and make sure the request is a valid page.
    num_pages = int(math.ceil(topic_num / float(TOPICS_PER_PAGE)))
    if num_pages < page:
        if page==1:
            return render_template('forum_board.html', board=board, forum=forum, topics=[],
                                   total_pages=num_pages, current_page=page,
                                   next=None, prev=None, links=[])
        abort(404)

    # Compile the list of topics we want displayed.
    display_topics = topics.skip((page - 1) * TOPICS_PER_PAGE).limit(TOPICS_PER_PAGE)
    if current_user.is_authenticated():
        read_topics = display_topics.filter(users_read_topic__in=[current_user.id]).scalar('id')
    else:
        read_topics = None

    # Find the links we want for the next/prev buttons if applicable.
    next_page = url_for('forum.view_board', page=page + 1, **board.get_url_info()) if page < num_pages \
        else None
    prev_page = url_for('forum.view_board', page=page - 1, **board.get_url_info()) if page > 1 and not num_pages == 1 \
        else None

    # Mash together a list of what pages we want linked to in the pagination bar.
    links = []
    for page_mod in range(-min(PAGINATION_VALUE_RANGE, page - 1), min(PAGINATION_VALUE_RANGE, num_pages-page) + 1):
        num = page + page_mod
        links.append({'num': num, 'url': url_for('forum.view_board', page=num, **board.get_url_info()), 'active': (num == page)})

    # Render it all out :D
    return render_template('forum_board.html', board=board, forum=forum, topics=display_topics, read_topics=read_topics,
                           total_pages=num_pages, current_page=page,
                           next=next_page, prev=prev_page, links=links)