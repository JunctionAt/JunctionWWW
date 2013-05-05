__author__ = 'HansiHE'

from .. import bans
from flask import render_template, abort
from flask_login import current_user
from blueprints.bans.ban_model import Ban
from blueprints.bans.appeal_model import Appeal
from blueprints.auth import login_required
import math

BANS_PER_PAGE = 15

@bans.route('/a/bans/your/', defaults={'page': 1})
@bans.route('/a/bans/your/<int:page>')
@login_required
def your_bans(page):

    bans = Ban.objects(username=current_user.name).order_by('-time')
    ban_num = len(bans)

    if not ban_num:
        return render_template('no_result_bans.html', message="You have no bans.")

    #Pagination logic begin
    num_pages = math.ceil(ban_num/float(BANS_PER_PAGE))
    if num_pages < page:
        abort(404)

    display_bans = bans.skip((page-1)*BANS_PER_PAGE).limit(BANS_PER_PAGE)
    location_info = "Page %i/%i, %i results with %i results per page" % (page, num_pages, ban_num, BANS_PER_PAGE)
    next_button = page < num_pages
    previous_button = page >= num_pages and not num_pages == 1
    #Pagination logic end

    return render_template(
        'bans_index.html',
        view="bans.your_bans",
        bans=display_bans,
        location_info=location_info,
        next_button=next_button,
        previous_button=previous_button,
        current_page=page
    )

@bans.route('/a/bans/created/', defaults={'page': 1})
@bans.route('/a/bans/created/<int:page>')
@login_required
def created_bans(page):
    bans = Ban.objects(issuer=current_user.name).order_by('-time')
    ban_num = len(bans)

    if not ban_num:
        return render_template('no_result_bans.html', message="No bans found")

    num_pages = math.ceil(ban_num/float(BANS_PER_PAGE))
    if num_pages < page:
        abort(404)

    display_bans = bans.skip((page-1)*BANS_PER_PAGE).limit(BANS_PER_PAGE)
    location_info = "Page %i/%i, %i results with %i results per page" % (page, num_pages, ban_num, BANS_PER_PAGE)
    next_button = page < num_pages
    previous_button = page >= num_pages and not num_pages == 1

    return render_template(
        'bans_index.html',
        view="bans.created_bans",
        bans=display_bans,
        location_info=location_info,
        next_button=next_button,
        previous_button=previous_button,
        current_page=page
    )

@bans.route('/a/bans/list/', defaults={'page': 1})
@bans.route('/a/bans/list/<int:page>')
def bans_index(page):

    if page == 0:
        abort(404)

    bans = Ban.objects(active=True).order_by('-time')
    ban_num = len(bans)

    num_pages = math.ceil(ban_num/float(BANS_PER_PAGE))
    if num_pages < page:
        if page==1:
            return render_template('no_result_bans.html', message='No bans found.')
        abort(404)

    display_bans = bans.skip((page-1)*BANS_PER_PAGE).limit(BANS_PER_PAGE)
    location_info = "Page %i/%i, %i results with %i results per page" % (page, num_pages, ban_num, BANS_PER_PAGE)
    next_button = page < num_pages
    previous_button = page > 1 and not num_pages == 1

    return render_template(
        'bans_index.html',
        view="bans.bans_index",
        bans=display_bans,
        location_info=location_info,
        next_button=next_button,
        previous_button=previous_button,
        current_page=page
    )