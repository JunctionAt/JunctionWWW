import flask
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

@flask.current_app.context_processor
def inject_notifications():
    return dict(notifications=__notifications__)

@flask.current_app.before_request
def populate_notifications(*args):
    while len(__notifications__): __notifications__.pop()
    if User.current_user:
        # Show notifications
        for module, notifications in reduce(
            lambda modules, notification:
                dict(modules.items() + [(notification.module, modules.get(notification.module, list()) + [notification])]),
            User.current_user.notifications, dict()).iteritems():
            notify(module, notifications)

@notification(name='player_notifications')
def show(notification):
    __notifications__.append(notification)

__notifications__ = list()
