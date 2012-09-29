import flask
from flask import url_for, render_template
import sqlalchemy
import sqlalchemy.orm
from sqlalchemy.orm import relation
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import *
from sqlalchemy import Column
from flask_login import current_user
from yell import notify
from yell.decorators import notification

from blueprints.base import Base
from blueprints.auth.user_model import User
from blueprints.player_profiles import Profile

class Notification(Base):
    """DB table to store notifications"""

    __tablename__ = 'player_notifications'
    user_name = Column(String(16), ForeignKey(User.name), primary_key=True)
    module = Column(String(32), primary_key=True)
    type = Column(String(16), primary_key=True)
    from_ = Column('from', String(16), primary_key=True)
    message = Column(String(256))
    user = relation(User, backref='notifications')

player_notifications = flask.Blueprint('player_notifications', __name__, template_folder='templates')

@player_notifications.route('/notifications')
def show_notifications():
    return render_template('show_notifications.html', player_notifications=User.current_user.notifications)

@flask.current_app.context_processor
def inject_notifications():
    return dict(notifications=__notifications__)

@flask.current_app.before_request
def populate_notifications(*args):
    while len(__notifications__): __notifications__.pop()
    if flask.request.path == url_for('player_notifications.show_notifications'): return
    if User.current_user:
        # Show notifications
        for module, notifications in by_module(User.current_user.notifications).iteritems():
            notify(module, notifications)

def by_module(notifications):
    return reduce(lambda modules, notification:
                      dict(modules.items() + [(notification.module, modules.get(notification.module, list()) + [notification])]),
                  notifications, dict())

@notification(name='player_notifications')
def show(notification):
    __notifications__.append(notification)

__notifications__ = list()
