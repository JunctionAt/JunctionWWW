import flask_login
import datetime

from mongoengine import *

class User(Document, flask_login.UserMixin, object):

    name = StringField(primary_key=True, required=True)
    hash = StringField(required=True)
    mail = StringField()
    registered = DateTimeField(default=datetime.datetime.utcnow())
    verified = BooleanField(default=False)

    avatar_type = IntField()

    #Note for whoever: Most permissions should be added through groups, not adding nodes directly to users.
    #The permissions list should ONLY be used in very specific cases.
    role_groups = ListField(ReferenceField('Role_Group', dbref=False))
    roles = ListField(StringField())

    meta = {
        'collection': 'users'
    }

    def get_id(self):
        return self.name

    def __repr__(self):
        return self.name

class Token(Document):

    token = StringField(required=True)
    name = StringField(primary_key=True, required=True)
    hash = StringField(required=True)
    mail = StringField()
    ip = StringField(required=True)
    expires = DateTimeField(required=True)

    meta = {
        'collection': 'tokens'
    }

#from blueprints.base import Base, session, db
#
#class User(Base, flask_login.UserMixin, object):
#
#    __tablename__ = 'users'
#    name = db.Column(db.String(16), primary_key=True)
#    hash = db.Column(db.String(100))
#    mail = db.Column(db.String(60))
#    registered = db.Column(db.DateTime, default=datetime.datetime.utcnow)
#    verified = db.Column(db.Boolean)
#
#    def get_id(self):
#        return self.name
#
#    def __repr__(self):
#        return self.name
#
#class Token(Base):
#
#    __tablename__ = 'tokens'
#    token = db.Column(db.CHAR(6), primary_key=True)
#    name = db.Column(db.String(16), db.ForeignKey(User.name), index=True)
#    hash = db.Column(db.String(100), index=True)
#    mail = db.Column(db.String(60))
#    ip = db.Column(db.String(39))
#    expires = db.Column(db.TIMESTAMP(), default=datetime.datetime.utcnow)
#    user = db.relation(User, backref='tokens')