import flask
import flask_login
import sqlalchemy.orm
import datetime

from blueprints.base import Base, session, db


class User(Base, flask_login.UserMixin, object):

    __tablename__ = 'users'
    name = db.Column(db.String(16), primary_key=True)
    hash = db.Column(db.String(100))
    mail = db.Column(db.String(60))
    registered = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    verified = db.Column(db.Boolean)
    
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
    token = db.Column(db.CHAR(6), primary_key=True)
    name = db.Column(db.String(16), index=True)
    hash = db.Column(db.String(100), index=True)
    mail = db.Column(db.String(60))
    ip = db.Column(db.String(39))
    expires = db.Column(db.TIMESTAMP(), default=datetime.datetime.utcnow)
