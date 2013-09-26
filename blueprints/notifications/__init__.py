__author__ = 'HansiHE'

from flask import Blueprint, request, render_template, abort, send_file, flash, redirect, url_for, current_app
from blueprints.auth import login_required
from flask_login import current_user
import json
import markdown
from notification_model import BaseNotification


blueprint = Blueprint('notifications', __name__, template_folder='templates')

notification_renderers = {}


class notification_renderer(object):
    def __init__(self, module):
        self.module = module
    def __call__(self, func):
        notification_renderers[self.module] = func


def get_notifications(user):
    return BaseNotification.objects(receiver=user.name)


def get_previews(user, num):
    return BaseNotification.objects(receiver=user.name).order_by('-date').limit(num)


def get_num(user):
    return len(BaseNotification.objects(receiver=user.name))


@current_app.context_processor
def inject_notifications():

    return dict(
        get_notifications=get_notifications,
        get_notifications_previews=get_previews,
        get_notifications_num=get_num
    )


@login_required
@blueprint.route('/notifications')
def notifications_view():
    return render_template('notifications_view.html', notifications=get_notifications(current_user))

@login_required
@blueprint.route('/notifications/delete/<string:id>/')
def notification_delete(id):
    notification = BaseNotification.objects(id=id).first()
    if notification is None:
        abort(404)
    if not notification.receiver.id == current_user.id:
        abort(404)
    if not notification.deletable:
        abort(404)

    notification.delete()

    return redirect(url_for('notifications.notifications_view'))

@blueprint.route('/nsendtest')
def test_send_notification():
    curr = BaseNotification(receiver=current_user.to_dbref(), sender_type=1, sender_user=current_user.to_dbref(), preview="A testable notification :D", deletable=True, type="test", module="test")
    curr.save()
    return 'yep'