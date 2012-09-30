import flask
import flask_login
from sqlalchemy import Column
from sqlalchemy.types import *
import sqlalchemy.orm
import datetime

from sqlalchemy.dialects import mysql

from blueprints.base import Base, session


class User(Base, flask_login.UserMixin, object):

    __tablename__ = 'users'
    name = Column(String(16), primary_key=True)
    hash = Column(String(100))
    mail = Column(String(60))
    registered = Column(DateTime, default=datetime.datetime.utcnow)
    verified = Column(Boolean)
    
    def get_id(self):
        return self.name

    def get_name(self):
        return self.name
        
    def is_active(self):
        return self.verified

    def __repr__(self):
        return self.name
    
class Token(Base):

    __tablename__ = 'tokens'
    token = Column(CHAR(6), primary_key=True)
    name = Column(String(16), index=True)
    hash = Column(String(100), index=True)
    mail = Column(String(60))
    ip = Column(String(39))
    expires = Column(mysql.TIMESTAMP(), default=datetime.datetime.utcnow)
