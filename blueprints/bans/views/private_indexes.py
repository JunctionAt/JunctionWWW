__author__ = 'HansiHE'

from .. import bans
from flask import render_template, abort
from flask_login import current_user
from blueprints.bans.ban_model import Ban
from blueprints.bans.appeal_model import Appeal
from blueprints.auth import login_required
import math

"""
This file should contain every page that indexes bans and appeals privately on a per-user basis.
"""

BANS_PER_PAGE = 10

@bans.route('/a/bans/your/', defaults={'page': 1})
@bans.route('/a/bans/your/<int:page>')
@login_required
def your_bans(page):

    bans = Ban.objects(username=current_user.name).order_by('-time')
    ban_num = len(bans)

    if not ban_num:
        return render_template('no_result_bans.html', message="You have no bans.")

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