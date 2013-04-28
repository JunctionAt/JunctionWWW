__author__ = 'HansiHE'

from mongoengine import *
from blueprints.auth.user_model import User

class Notification(Document):

    uid = SequenceField(required=True)

    receiver = ReferenceField(User, dbref=False, required=True) #The receiver of the notification. This is required.

    sender_type = IntField(required=True, default=0) #0 or None: No sender defined. 1: Sent by sender_user. 2: The text in the sender field is sender_text. 3: Same as 2, but the sender text is linked to sender_link.
    sender_user = ReferenceField(User, dbref=False)
    sender_text = StringField()
    sender_link = StringField()
    sender_data = StringField()

    preview = StringField(required=True) #The data we should use in previews.

    deletable = BooleanField(default=False) #Specifies if the notification should be deletable through the standard delete button. You can hook onto this event.

    module = StringField(required=True) #Required, defines where it came from.
    # noinspection PyShadowingBuiltins
    type = StringField() #May be used for future sorting/hiding of certain types.
    data = DictField() #When creating the notification, the creator may supply custom data.

    meta = {
        'collection': 'notifications',
        'indexed' : [ 'receiver', 'module', 'type' ]
    }