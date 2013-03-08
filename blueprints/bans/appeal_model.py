__author__ = 'HansiHE'

from mongoengine import *
import datetime
from ban_model import Ban
from blueprints.auth.user_model import User
import shortuuid

class AppealEdit(EmbeddedDocument):

    text = StringField(required=True)
    user = ReferenceField(User, dbref=False, required=True)
    time = DateTimeField(default=datetime.datetime.utcnow, required=True)

class AppealReply(Document):

    appeal = ReferenceField('Appeal', dbref=False, required=True)
    uid = SequenceField(unique=True)

    created = DateTimeField(default=datetime.datetime.utcnow, required=True)
    edited = DateTimeField()

    creator = ReferenceField(User, dbref=False, required=True)
    editor = ReferenceField(User, dbref=False)

    text = StringField(required=True)

    edits = ListField(EmbeddedDocumentField(AppealEdit))

    meta = {
        'collection': 'appeal_responses',
        'indexed': [ 'appeal', 'uid' ]
    }

class Appeal(Document):

    ban = ReferenceField(Ban, dbref=False, required=True)
    created = DateTimeField(default=datetime.datetime.utcnow, required=True)

    replies = ListField(ReferenceField(AppealReply, dbref=False))
    last = DateTimeField(default=datetime.datetime.utcnow, required=True)

    #0:open - 1:hard closed for timeframe - 2:hard closed forever
    state = IntField(default=0)
    locked_until = DateTimeField()

    meta = {
        'collection': 'appeals',
        'indexed': [ 'ban' ]
    }