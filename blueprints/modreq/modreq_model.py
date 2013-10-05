from mongoengine import *
import datetime

class ModReqP(Document):

    uid = SequenceField(unique=True)
    username = StringField(required=True)
    request = StringField(required=True)
    location = StringField(required=True)
    status = StringField(required=True)
    time = DateTimeField(default=datetime.datetime.utcnow)

    handled_by = StringField()
    close_message = StringField()
    close_time = DateTimeField()

    def __repr__(self):
        return self.uid

    meta = {
        'collection': 'modreq_p',
        'indexed': [ 'uid' ]
    }

class ModReqS(Document):

    uid = SequenceField(unique=True)
    username = StringField(required=True)
    request = StringField(required=True)
    location = StringField(required=True)
    status = StringField(required=True)
    time = DateTimeField(default=datetime.datetime.utcnow)

    handled_by = StringField()
    close_message = StringField()
    close_time = DateTimeField()

    def __repr__(self):
        return self.uid

    meta = {
        'collection': 'modreq_s',
        'indexed': [ 'uid' ]
    }

class ModReqE(Document):

    uid = SequenceField(unique=True)
    username = StringField(required=True)
    request = StringField(required=True)
    location = StringField(required=True)
    status = StringField(required=True)
    time = DateTimeField(default=datetime.datetime.utcnow)

    handled_by = StringField()
    close_message = StringField()
    close_time = DateTimeField()

    def __repr__(self):
        return self.uid

    meta = {
        'collection': 'modreq_e',
        'indexed': [ 'uid' ]
    }
