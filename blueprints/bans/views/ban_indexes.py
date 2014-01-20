__author__ = 'HansiHE'

from .. import bans
from flask import render_template, abort, url_for
from flask_login import current_user
from blueprints.bans.ban_model import Ban
from blueprints.auth import login_required
from blueprints.auth.util import require_permissions
import math

BANS_PER_PAGE = 15
PAGINATION_VALUE_RANGE = 3

@bans.route('/a/bans/your/', defaults={'page': 1})
@bans.route('/a/bans/your/<int:page>')
@login_required
def your_bans(page):

    if page == 0:
        abort(404)

    bans = Ban.objects(username=current_user.name).order_by('-time')
    ban_num = len(bans)

    num_pages = int(math.ceil(ban_num / float(BANS_PER_PAGE)))
    if num_pages < page:
        if page==1:
            return render_template('no_result_bans.html', message="You have no bans.", view="bans.your_bans", title="Your Bans")
        abort(404)

    display_bans = bans.skip((page - 1) * BANS_PER_PAGE).limit(BANS_PER_PAGE)
    # Find the links we want for the next/prev buttons if applicable.
    next_page = url_for('bans.your_bans', page=page + 1) if page < num_pages \
        else None
    prev_page = url_for('bans.your_bans', page=page - 1) if page > 1 and not num_pages == 1 \
        else None

    # Mash together a list of what pages we want linked to in the pagination bar.
    links = []
    for page_mod in range(-min(PAGINATION_VALUE_RANGE, page - 1), min(PAGINATION_VALUE_RANGE, num_pages-page) + 1):
        num = page + page_mod
        links.append({'num': num, 'url': url_for('bans.your_bans', page=num), 'active': num != page})


    return render_template(
        'bans_index.html',
        view="bans.your_bans",
        base_title="Your Bans",
        bans=display_bans,
        total_pages=num_pages,
        next=next_page,
        prev=prev_page,
        links=links
    )

@bans.route('/a/bans/created/', defaults={'page': 1})
@bans.route('/a/bans/created/<int:page>')
@login_required
def created_bans(page):
    if not current_user.has_permission('bans.create'):
        abort(403)

    if page == 0:
        abort(404)

    bans = Ban.objects(issuer=current_user.name).order_by('-time')
    ban_num = len(bans)

    num_pages = int(math.ceil(ban_num / float(BANS_PER_PAGE)))
    if num_pages < page:
        if page==1:
            return render_template('no_result_bans.html', message="No bans found.", view="bans.created_bans", title="Bans you've made")
        abort(404)

    display_bans = bans.skip((page - 1) * BANS_PER_PAGE).limit(BANS_PER_PAGE)
    # Find the links we want for the next/prev buttons if applicable.
    next_page = url_for('bans.created_bans', page=page + 1) if page < num_pages \
        else None
    prev_page = url_for('bans.created_bans', page=page - 1) if page > 1 and not num_pages == 1 \
        else None

    # Mash together a list of what pages we want linked to in the pagination bar.
    links = []
    for page_mod in range(-min(PAGINATION_VALUE_RANGE, page - 1), min(PAGINATION_VALUE_RANGE, num_pages-page) + 1):
        num = page + page_mod
        links.append({'num': num, 'url': url_for('bans.created_bans', page=num), 'active': num != page})

    return render_template(
        'bans_index.html',
        view="bans.created_bans",
        base_title="Bans you've made",
        bans=display_bans,
        total_pages=num_pages,
        next=next_page,
        prev=prev_page,
        links=links
    )

@bans.route('/a/bans/list/', defaults={'page': 1})
@bans.route('/a/bans/list/<int:page>')
def bans_index(page):

    if page == 0:
        abort(404)

    bans = Ban.objects(active=True).order_by('-time')
    ban_num = len(bans)

    num_pages = int(math.ceil(ban_num / float(BANS_PER_PAGE)))
    if num_pages < page:
        if page==1:
            return render_template('no_result_bans.html', message="No bans found.", view="bans.bans_index", title="All bans")
        abort(404)

    display_bans = bans.skip((page - 1) * BANS_PER_PAGE).limit(BANS_PER_PAGE)
    # Find the links we want for the next/prev buttons if applicable.
    next_page = url_for('bans.bans_index', page=page + 1) if page < num_pages \
        else None
    prev_page = url_for('bans.bans_index', page=page - 1) if page > 1 and not num_pages == 1 \
        else None

    # Mash together a list of what pages we want linked to in the pagination bar.
    links = []
    for page_mod in range(-min(PAGINATION_VALUE_RANGE, page - 1), min(PAGINATION_VALUE_RANGE, num_pages-page) + 1):
        num = page + page_mod
        links.append({'num': num, 'url': url_for('bans.bans_index', page=num), 'active': num != page})

    return render_template(
        'bans_index.html',
        view="bans.bans_index",
        base_title="All bans",
        bans=display_bans,
        total_pages=num_pages,
        next=next_page,
        prev=prev_page,
        links=links
    )
