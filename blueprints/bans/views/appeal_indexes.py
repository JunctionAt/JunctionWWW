__author__ = 'HansiHE'

from .. import bans
from flask import render_template, abort
from flask_login import current_user
from blueprints.bans.ban_model import Ban
from blueprints.bans.appeal_model import Appeal
from blueprints.auth import login_required
import math

APPEALS_PER_PAGE = 20

@bans.route('/a/appeal/list/', defaults={'page': 1})
@bans.route('/a/appeal/list/<int:page>')
def appeals_index(page):

    if page == 0:
        abort(404)

    appeals = Appeal.objects().order_by('-created')
    appeal_num = len(appeals)

    num_pages = math.ceil(appeal_num/float(APPEALS_PER_PAGE))
    if num_pages < page:
        if page==1:
            return render_template('no_result_bans.html', message='No appeals found.')
        abort(404)

    display_appeals = appeals.skip((page-1)*APPEALS_PER_PAGE)
    location_info = "Page %i/%i, %i results with %i results per page" % (page, num_pages, appeal_num, APPEALS_PER_PAGE)
    next_button = page < num_pages
    previous_button = page > 1 and not num_pages == 1

    return render_template(
        'appeals_index.html',
        appeals=display_appeals,
        location_info=location_info,
        next_button=next_button,
        previous_button=previous_button,
        current_page=page
    )