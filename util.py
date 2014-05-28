import datetime
import arrow


def pretty_date_since(time=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    now = datetime.datetime.utcnow()
    if type(time) is int:
        diff = now - datetime.datetime.fromtimestamp(time)
    elif isinstance(time, datetime.datetime):
        diff = now - time
    elif not time:
        diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return "a minute ago"
        if second_diff < 3600:
            return str(second_diff / 60) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str(second_diff / 3600) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        num = day_diff / 7
        if num == 1:
            return "a week ago"
        else:
            return str(num) + " weeks ago"
    if day_diff < 365:
        num = day_diff / 30
        if num == 1:
            return "a month ago"
        else:
            return str(day_diff / 30) + " months ago"

    num = day_diff / 365
    if num == 1:
        return "a year ago"
    else:
        return str(day_diff / 365) + " years ago"


def full_date(time, classes=""):  # <span data-tooltip title="{{ alt.last_login }}" class="has-tip {% if alt.last_login < ban_object.time %}alert{% else %}secondary{% endif %} label">{{ alt.last_login|pretty_date }}</span>
    pretty_time = arrow.get(time).humanize()
    return '<span data-tooltip title="' + \
           time.strftime("%b %d %Y - %H:%M") + \
           '" class="' + \
           classes + '">' + \
           pretty_time + \
           '</span>'
