__author__ = 'HansiHE'

from flask import request, abort
import datetime
import json

from .. import blueprint


@blueprint.route('/calendar/<string:calendar_name>/<string:feed_name>.json')
def calendar_feed(calendar_name, feed_name):
    start_raw = request.args.get('start', None)
    if not start_raw:
        abort(400)
    try:
        start = datetime.datetime.fromtimestamp(float(start_raw))
    except ValueError:
        abort(400)

    end_raw = request.args.get('end', None)
    if not end_raw:
        abort(400)
    try:
        end = datetime.datetime.fromtimestamp(float(end_raw))
    except ValueError:
        abort(400)

    return json.dumps([{'title': "Test event for teh funnz", 'start': str(datetime.datetime.utcnow())}])