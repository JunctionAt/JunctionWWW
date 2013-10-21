__author__ = 'HansiHE'

from .. import bans
from flask import render_template, abort, url_for
from flask_login import current_user
from blueprints.bans.ban_model import Ban
from blueprints.bans.appeal_model import Appeal
from blueprints.auth import login_required
import math

APPEALS_PER_PAGE = 15
PAGINATION_VALUE_RANGE = 3

@bans.route('/a/appeal/list/', defaults={'page': 1})
@bans.route('/a/appeal/list/<int:page>')
def appeals_index(page):

    if page == 0:
        abort(404)

    appeals = Appeal.objects().order_by('-created')
    appeal_num = len(appeals)

    num_pages = int(math.ceil(appeal_num / float(APPEALS_PER_PAGE)))
    if num_pages < page:
        if page==1:
            return render_template('no_result_bans.html', message="No appeals found.", view="bans.appeals_index", title="All appeals")
        abort(404)

    display_appeals = appeals.skip((page - 1) * APPEALS_PER_PAGE).limit(APPEALS_PER_PAGE)
    # Find the links we want for the next/prev buttons if applicable.
    next_page = url_for('bans.appeals_index', page=page + 1) if page < num_pages \
        else None
    prev_page = url_for('bans.appeals_index', page=page - 1) if page > 1 and not num_pages == 1 \
        else None

    # Mash together a list of what pages we want linked to in the pagination bar.
    links = []
    for page_mod in range(-min(PAGINATION_VALUE_RANGE, page - 1), min(PAGINATION_VALUE_RANGE, num_pages-page) + 1):
        num = page + page_mod
        links.append({'num': num, 'url': url_for('bans.appeals_index', page=num), 'active': (num == page)})

    return render_template(
        'appeals_index.html',
        view="bans.appeals_index",
        title="All appeals",
        appeals=display_appeals,
        total_pages=num_pages,
        next=next_page,
        prev=prev_page,
        links=links
    )
