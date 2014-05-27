__author__ = 'HansiHE'

from flask import render_template, current_app

from .. import blueprint


@blueprint.route('/calendar/', defaults={'calendar_name': current_app.config.get('DEFAULT_CALENDAR')})
@blueprint.route('/calendar/<string:calendar_name>/')
def view_calendar(calendar_name):
    return render_template('calendar_view.html', feed_urls=['/calendar/wat/main.json'], title="Calendar")
