__author__ = 'HansiHE'

from flask import render_template
from .. import blueprint


@blueprint.route('/calendar')
def view_calendar():
    return render_template('calendar_view.html', feed_urls=['/calendar/feed.json'])