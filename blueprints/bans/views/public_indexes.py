__author__ = 'HansiHE'

from .. import bans
from flask import render_template, abort
from blueprints.bans.ban_model import Ban
from blueprints.bans.appeal_model import Appeal
import math

"""
This file should contain every page that indexes bans and appeals publicly.
"""


BANS_PER_PAGE = 10
APPEALS_PER_PAGE = 10

@bans.route('/a/bans/list/', defaults={'page': 1})
@bans.route('/a/bans/list/<int:page>')
def bans_index(page):

    bans = Ban.objects(active=True).order_by('-time')
    ban_num = len(bans)

    num_pages = math.ceil(ban_num/float(BANS_PER_PAGE))
    if num_pages < page:
        abort(404)

    display_bans = bans.skip((page-1)*BANS_PER_PAGE).limit(BANS_PER_PAGE)
    location_info = "Page %i/%i, %i results with %i results per page" % (page, num_pages, ban_num, BANS_PER_PAGE)
    next_button = page < num_pages
    previous_button = page >= num_pages and not num_pages == 1

    return render_template(
        'bans_index.html',
        bans=display_bans,
        location_info=location_info,
        next_button=next_button,
        previous_button=previous_button,
        current_page=page
    )

@bans.route('/a/appeals/list/', defaults={'page': 1})
@bans.route('/a/appeals/list/<int:page>')
def appeals_index(page):

    appeals = Appeal.objects().order_by('-created')
    appeal_num = len(appeals)

    num_pages = math.ceil(appeal_num/float(APPEALS_PER_PAGE))
    if num_pages < page:
        abort(404)

    display_appeals = appeals.skip((page-1)*APPEALS_PER_PAGE)
    location_info = "Page %i/%i, %i results with %i results per page" % (page, num_pages, appeal_num, APPEALS_PER_PAGE)
    next_button = page < num_pages
    previous_button = page >= num_pages and not num_pages == 1

    return render_template(
        'appeals_index.html',
        appeals=display_appeals,
        location_info=location_info,
        next_button=next_button,
        previous_button=previous_button,
        current_page=page
    )