import flask
import flask_login
from sqlalchemy import Column
from sqlalchemy.types import *
import sqlalchemy.orm

from blueprints.base import Base


class User(Base, object):

    __tablename__ = 'users'
    name = Column(String(16), primary_key=True)
    hash = Column(String(100))
    mail = Column(String(60))
    registered = Column(DateTime)
    verified = Column(Boolean)
    
    def __repr__(self):
        return self.name
    
    @flask.current_app.context_processor
    def inject_user():
        return dict(current_user=User.current_user)
    
    # Static class property
    def _current_user(self, cls, owner):
        if User._user is False:
            if flask_login.current_user:
                User._user = sqlalchemy.orm.sessionmaker(flask.current_app.config['ENGINE'])() \
                    .query(User) \
                    .filter(User.name==flask_login.current_user.name) \
                    .one()
            else:
                User._user = None
        return User._user
    
    current_user = type('property', (property,), dict(__get__=_current_user))()


    @staticmethod
    @flask.current_app.before_request
    def reset_current_user():
        setattr(User, '_user', False)
