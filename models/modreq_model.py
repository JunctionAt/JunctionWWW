from mongoengine import *
import datetime


class ModReq(Document):

    uid = SequenceField(unique=True)
    server = StringField(required=True)
    username = StringField(required=True)
    request = StringField(required=True)
    location = StringField(required=True)
    status = StringField(required=True, choices=["open", "claimed", "closed"])
    time = DateTimeField(required=True, default=datetime.datetime.utcnow)

    elevate_group = StringField()

    handled_by = StringField()
    close_message = StringField()
    close_time = DateTimeField()

    def __repr__(self):
        return self.uid

    meta = {
        'collection': 'modreq',
        'indexed': ['uid']
    }
