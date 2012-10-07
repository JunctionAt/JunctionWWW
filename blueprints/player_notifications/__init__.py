"""
Notifications
=============

Persistant player notification system.
Notifications do not go away until they are actioned upon.
Currently, only player group invitations will spawn notifications.
"""

import flask
from flask import Blueprint, url_for, render_template, jsonify, current_app
import flask_login
import sqlalchemy
import sqlalchemy.orm
from yell import notify
from yell.decorators import notification
import markdown

from blueprints.base import Base, db
from blueprints.auth.user_model import User
from blueprints.player_profiles import Profile
from blueprints.api import apidoc

class Notification(Base):
    """DB table to store notifications"""

    __tablename__ = 'player_notifications'
    user_name = db.Column(db.String(16), db.ForeignKey(User.name), primary_key=True)
    module = db.Column(db.String(32), primary_key=True)
    type = db.Column(db.String(16), primary_key=True)
    from_ = db.Column('from', db.String(16), primary_key=True)
    message = db.Column(db.String(256))
    user = db.relation(User, backref='notifications')

player_notifications = Blueprint('player_notifications', __name__, template_folder='templates')

@apidoc(__name__, player_notifications, '/notifications.json', endpoint='show_notifications', defaults=dict(ext='json'))
def show_notifications_api(ext):
    """Returns an object with a ``notifications`` key. The notifications are a list of objects with ``module``, ``type``, ``from``, and ``message`` strings."""

@player_notifications.route('/notifications', defaults=dict(ext='html'), endpoint='show_notifications')
@flask_login.login_required
def show_notifications(ext):
    if ext == 'json': return jsonify(
        notifications=map(lambda notification: {
                'module': notification.module,
                'type': notification.type,
                'from': notification.from_,
                'message': markdown.markdown(notification.message)
                }, flask_login.current_user.notifications))
    return render_template('show_notifications.html', player_notifications=flask_login.current_user.notifications)

@flask.current_app.context_processor
def inject_notifications():
    return dict(get_notifications=get_notifications)

def by_module(notifications):
    return reduce(lambda modules, notification:
                      dict(modules.items() + [(notification.module, modules.get(notification.module, list()) + [notification])]),
                  notifications, dict())

@notification(name='player_notifications')
def show(notification):
    __notifications__.append(notification)

__notifications__ = list()

def get_notifications():
    while len(__notifications__): __notifications__.pop()
    if flask.request.path == url_for('player_notifications.show_notifications'): return
    if flask_login.current_user.is_authenticated():
        # Show notifications
        for module, notifications in by_module(flask_login.current_user.notifications).iteritems():
            notify(module, notifications)
    return __notifications__
