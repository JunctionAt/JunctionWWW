__author__ = 'HansiHE'

from mongoengine import *
from blueprints.auth.user_model import User

class Notification(Document):

    user = ReferenceField(User, dbref=False, required=True)
    message = StringField(required=True)
    sender = ReferenceField(User, dbref=False)
    type = StringField()
    module = StringField()

    meta = {
        'collection': 'notifications'
    }

    def get_renderer(self):
        pass