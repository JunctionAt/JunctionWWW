#from flask import Flask
#from blueprints.base import Base, session, db
from blueprints.auth import User
from mongoengine import *
import datetime

class Ban(Document):

    uid = SequenceField(unique=True)
    issuer = ReferenceField(User, dbref=False, required=True)
    username = StringField(required=True)
    reason = StringField(required=True)
    server = StringField(required=True)
    time = DateTimeField(default=datetime.datetime.utcnow)
    active = BooleanField(default=True)

    def get_time(self):
        return self.time.strftime("%s")

    def __repr__(self):
        return self.id

    meta = {
        'collection': 'bans'
    }

class Note(Document):

    uid = SequenceField(unique=True)
    issuer = ReferenceField(User, dbref=False, required=True)
    username = StringField(required=True)
    note = StringField(required=True)
    server = StringField(required=True)
    time = DateTimeField(default=datetime.datetime.utcnow)
    active = BooleanField(default=True)

    def get_time (self):
        return self.time.strftime("%s")

    def __repr__ (self):
        return self.id

    meta = {
        'collection': 'notes'
    }