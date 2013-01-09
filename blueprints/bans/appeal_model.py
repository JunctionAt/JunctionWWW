__author__ = 'HansiHE'

from mongoengine import *
import datetime
from ban_model import Ban
from blueprints.auth.user_model import User

class AppealReply(EmbeddedDocument):

    created = DateTimeField(default=datetime.datetime.utcnow, required=True)
    creator = ReferenceField(User, dbref=False, required=True)
    text = StringField(required=True)

class Appeal(Document):

    ban = ReferenceField(Ban, dbref=False, required=True)
    created = DateTimeField(default=datetime.datetime.utcnow, required=True)

    replies = ListField(EmbeddedDocumentField(AppealReply))

    #0:open - 1:soft closed - 2:hard closed for timeframe - 3:hard closed forever
    state = IntField(default=0)
    unlock_time = DateTimeField()