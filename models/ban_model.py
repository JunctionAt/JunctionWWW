#from flask import Flask
#from blueprints.base import Base, session, db
from mongoengine import *
import datetime

from models.user_model import User


class AppealEdit(EmbeddedDocument):
    text = StringField(required=True)
    user = ReferenceField(User, dbref=False, required=True)
    time = DateTimeField(default=datetime.datetime.utcnow, required=True)


class AppealReply(Document):
    ban = ReferenceField('Ban', dbref=False, required=True)
    uid = SequenceField(unique=True)

    created = DateTimeField(default=datetime.datetime.utcnow, required=True)
    edited = DateTimeField()

    creator = ReferenceField(User, dbref=False, required=True)
    editor = ReferenceField(User, dbref=False)

    text = StringField(required=True)

    edits = ListField(EmbeddedDocumentField(AppealEdit))

    hidden = BooleanField(default=False)

    meta = {
        'collection': 'appeal_responses',
        'indexed': ['appeal', 'uid']
    }


class Appeal(EmbeddedDocument):
    replies = ListField(ReferenceField(AppealReply, dbref=False))
    last = DateTimeField(default=datetime.datetime.utcnow, required=True)

    #0:open - 1:hard closed for timeframe - 2:hard closed forever
    state = StringField(choices=["open", "closed_time", "closed_forever"], required=True, default="open")

    unlock_time = DateTimeField()
    unlock_by = StringField()


class Ban(Document):
    """
    Issuer should be stored as a user, target as player.
    """
    uid = SequenceField(unique=True)

    target = ReferenceField('MinecraftPlayer', dbref=False, required=True)
    issuer = ReferenceField('User', db_field="issuer", dbref=False, required=True)

    issuer_old = StringField(required=True, db_field="issuer_old")
    username = StringField(required=True)

    reason = StringField(required=True)
    server = StringField(required=True)
    time = DateTimeField(default=datetime.datetime.utcnow)
    active = BooleanField(default=True)

    removed_time = DateTimeField()
    removed_by = StringField()

    appeal = EmbeddedDocumentField('Appeal', required=True, default=Appeal)

    def __init__(self, *args, **kwargs):
        super(Ban, self).__init__(*args, **kwargs)
        self._process_ban()

    def _process_ban(self):
        if not self.active:
            return False
        if self.removed_time is not None and self.removed_time < datetime.datetime.utcnow():
            self.update(set__active=False)
            return False
        return True

    def get_time(self):
        return self.time.strftime("%s")

    def __repr__(self):
        return self.id

    meta = {
        'collection': 'bans',
        'indexed': ['uid', 'issuer_old', 'username', 'appeal']
    }


class Note(Document):
    uid = SequenceField(unique=True)

    target = ReferenceField('MinecraftPlayer', dbref=False, required=True)
    issuer = ReferenceField('User', db_field="issuer", dbref=False)

    issuer_old = StringField(required=True, db_field="issuer_old")
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
        'collection': 'notes',
        'indexed': [ 'uid', 'issuer', 'username' ]
    }