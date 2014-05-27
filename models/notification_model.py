__author__ = 'HansiHE'

from mongoengine import *
import datetime

from models.user_model import User


# Notification inheritance tree:
#
# BaseNotification
# - BasePlayerSenderNotification
# - - PMNotification
# - BaseCustomSenderNotification


class NoNotificationRendererNotification(Exception):
    pass


class BaseNotification(Document):

    receiver = StringField(required=True)

    date = DateTimeField(required=True, default=datetime.datetime.utcnow)
    deletable = BooleanField(default=False)

    read = BooleanField(default=False)
    deleted = BooleanField(default=False)

    @property
    def receiver_user(self):
        return User.objects(name=self.receiver).first()

    def render_notification(self):
        raise NoNotificationRendererNotification("No notification renderer for notification")

    def render_preview(self):
        raise NoNotificationRendererNotification("No preview renderer for notification")

    meta = {
        'allow_inheritance': True,
        'collection': 'notifications',
        'indexed': ['receiver', 'module', 'type']
    }


class BasePlayerSenderNotification(BaseNotification):

    sender = StringField(required=True)

    @property
    def sender_user(self):
        return User.objects(name=self.sender).first()


class PMNotification(BasePlayerSenderNotification):

    deletable = BooleanField(default=True)
    source = StringField()
    message = StringField(required=True)

    def render_preview(self):
        return "Mail from %s" % self.sender

    def render_notification(self):
        return self.message


class BaseCustomSenderNotification(BaseNotification):
    pass


# class Notification(Document):
#
#     receiver = ReferenceField(User, dbref=False, required=True)  # The receiver of the notification. This is required.
#
#     sender_type = IntField(required=True, default=0)  # 0 or None: No sender defined. 1: Sent by sender_user. 2: The text in the sender field is sender_text, sender_link as optional link.
#     sender_user = ReferenceField(User, dbref=False)
#     sender_text = StringField()
#     sender_link = StringField()
#     sender_data = StringField()
#
#     preview = StringField(required=True)  # The data we should use in previews.
#
#     render_type = IntField(required=True, default=0)  # 0 or None: Display 'text' in data as plaintext. 1: Display 'text' in data as markdown. 2: Display 'text' in data as HTML. 3: Call the render hook.
#
#     deletable = BooleanField(default=False)  #Specifies if the notification should be deletable through the standard delete button. You can hook onto this event.
#
#     module = StringField(required=True)  # Required, defines where it came from.
#     # noinspection PyShadowingBuiltins
#     type = StringField()  # May be used for future sorting/hiding of certain types.
#     data = DictField()  # When creating the notification, the creator may supply custom data.
#
#     date = DateTimeField(required=True, default=datetime.utcnow)
#
#     meta = {
#         'collection': 'notifications',
#         'indexed' : [ 'receiver', 'module', 'type' ]
#     }
#
#     def get_string_id(self):
#         return str(self.id)
