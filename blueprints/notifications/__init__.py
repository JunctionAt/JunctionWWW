__author__ = 'HansiHE'

from flask import Blueprint, request, render_template, abort, send_file, flash, redirect, url_for, current_app
from blueprints.auth import login_required
from flask_login import current_user
import json
import markdown
import notification_model

blueprint = Blueprint('notifications', __name__,
    template_folder='templates')

notification_renderers = {}

class notification_renderer(object):
    def __init__(self, module):
        self.module = module
    def __call__(self, func):
        notification_renderers[self.module] = func

def get_notifications(user):
    return notification_model.Notification.objects(receiver=user)

def get_previews(user):
    notification_model.Notification.objects(receiver=user).only("uid", "preview")

@current_app.context_processor
def inject_notifications():

    def get_current_notifications():
        return get_notifications(current_user.name)

    return dict(
        get_notifications=get_current_notifications,
        get_notifications_previews=get_previews
    )

@blueprint.route('/notifications')
def get_notifications_view():
    return render_template('notifications_view.html')
