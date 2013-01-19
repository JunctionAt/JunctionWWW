__author__ = 'HansiHE'

from flask import Blueprint, request, render_template, abort, send_file, flash, redirect, url_for, current_app
from blueprints.auth import login_required
from flask_login import current_user
import json
import markdown
import yell
import notification_model

blueprint = Blueprint('notifications', __name__,
    template_folder='templates')

accept_hooks = {}
deny_hooks = {}

class WebNotification(yell.Notification):
    name = "website"

    def notify(self, *args, **kwargs):
        user = kwargs.get("user")
        from_user = kwargs.get("from_user")
        type = kwargs.get("type")
        message = kwargs.get("message")

        if message is None or user is None:
            raise KeyError("One of the required arguments wasn't supplied.")

        notification = notification_model.Notification(
            user=user,
            from_user=from_user,
            message=message,
            type=type
        )
        notification.save()

class MailNotification(yell.Notification):
    name = "mail"

    def notify(self, *args, **kwargs):
        pass

#When hooking onto any of these, you should accept one argument, the database entry.

class on_accept(object):
    def __init__(self, name):
        self.name = name

    def __call__(self, f):
        accept_hooks.append(self.name)
        return f

class on_deny(object):
    def __init__(self, name):
        self.name = name

    def __call__(self, f):
        deny_hooks.append(self.name)
        return f

@blueprint.route('/notifications', defaults=dict(ext='html'), endpoint='show_notifications')
@login_required
def show_notifications(ext):
    if ext == 'json': return json.dumps({
        "notifications": map(lambda notification: {
            'user': notification.user,
            'type': notification.type,
            'from': notification.from_user,
            'message': markdown.markdown(notification.message)
        }, get_notifications())})
    return render_template('show_notifications.html', player_notifications=get_notifications())

@current_app.current_app.context_processor
def inject_notifications():
    return dict(get_notifications=get_notifications)

def get_notifications():
    if current_user.is_authenticated():
        return current_user.notifications
    return []