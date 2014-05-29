from flask import Blueprint, render_template, abort, redirect, url_for, current_app
from flask_login import current_user

from blueprints.auth import login_required
from models.notification_model import BaseNotification


blueprint = Blueprint('notifications', __name__, template_folder='templates')

notification_renderers = {}


class NotificationRenderer(object):
    def __init__(self, module):
        self.module = module

    def __call__(self, func):
        notification_renderers[self.module] = func


def get_notifications(user):
    return BaseNotification.by_receiver(user, deleted=False).order_by('-date')


def get_previews(user, num):
    return BaseNotification.by_receiver(user, read=False, deleted=False).order_by('-date').limit(num)


def get_num(user):
    return len(BaseNotification.by_receiver(user, read=False, deleted=False))


@current_app.context_processor
def inject_notifications():
    return dict(
        get_notifications=get_notifications,
        get_notifications_previews=get_previews,
        get_notifications_num=get_num
    )


@blueprint.route('/notifications')
@login_required
def notifications_view():
    return render_template('notifications_view.html', title="Notifications",
                           notifications=get_notifications(current_user._get_current_object()))


@blueprint.route('/notifications/mark/<string:id>/<string:mark>')
@login_required
def notification_mark(id, mark):
    notification = BaseNotification.objects(id=id).first()
    if notification is None:
        abort(404)
    if not notification.receiver.user == current_user._get_current_object():
        abort(404)

    if mark == 'read':
        notification.read = True
    elif mark == 'unread':
        notification.read = False
    else:
        abort(404)

    notification.save()

    return redirect(url_for('notifications.notifications_view'))
