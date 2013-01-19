__author__ = 'HansiHE'

from mongoengine import *
from blueprints.auth.user_model import User

class Notification(Document):

    user = ReferenceField(User, dbref=False, required=True)
    message = StringField(required=True)
    from_user = ReferenceField(User, dbref=False)
    type = StringField() #Default format is blueprintname.subname

    meta = {
        'collection': 'notifications'
    }