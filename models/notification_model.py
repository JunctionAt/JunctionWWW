from mongoengine import *
from mongoengine.signals import post_save
import datetime
from flask import render_template

from models.user_model import User
from models.player_model import MinecraftPlayer


class NoNotificationRendererException(Exception):
    pass


# Notifications sent or received by a ingame player should use this.
class PlayerTarget(EmbeddedDocument):

    # I don't like the way this is done, however as of right now this is the way that would be easiest to use from the
    # outside. This can not be done automatically, as we need express intent from the caller.
    def with_user(self):
        resolve_user(self)
        return self

    player = ReferenceField(MinecraftPlayer, required=True)

    # This is here to make queries faster and easier. We are listening on the post_save signal, and updating this.
    # Please note that this will often be null, as a minecraft player is not guaranteed to have a www account.
    user = ReferenceField(User, required=False)

    target_type = "player"

    def render_html(self):
        return self.player.mcname


# Notifications sent or received by a website user should use this.
class UserTarget(EmbeddedDocument):
    user = ReferenceField(User, required=True)

    target_type = "user"

    def render_html(self):
        return self.user.name


# Notifications sent by a internal entity (system) should use this.
class StaticTarget(EmbeddedDocument):
    name = StringField(required=True)

    target_type = "static"

    def render_html(self):
        return self.name


class BaseNotification(Document):
    """
    The base for all notifications on the website. This should not be used by itself, only subclassed.
    """

    receiver = GenericEmbeddedDocumentField(required=True, choices=[PlayerTarget, UserTarget])
    sender = GenericEmbeddedDocumentField(required=True, choices=[PlayerTarget, UserTarget, StaticTarget])

    date = DateTimeField(required=True, default=datetime.datetime.utcnow)

    read = BooleanField(default=False)
    deleted = BooleanField(default=False)

    def render_notification_listing(self):
        raise NoNotificationRendererException("No notification listing renderer for notification")

    @classmethod
    def by_receiver(cls, receiver, **kwargs):
        if isinstance(receiver, User):
            return cls.objects(__raw__={'receiver.user': receiver.id}, **kwargs)
        elif isinstance(receiver, MinecraftPlayer):
            return cls.objects(__raw__={'receiver.player': receiver.id}, **kwargs)
        else:
            raise TypeError("A receiver may only be a User or a MinecraftPlayer")

    meta = {
        'allow_inheritance': True,
        'collection': 'notifications',
        'indexed': ['receiver', 'module', 'type']
    }


def resolve_user(doc):
    user = User.objects(minecraft_player=doc.player).first()

    if doc.user != user:
        document.user = user


def handle_user_update(sender, document, created):
    sent_notifications = BaseNotification.objects(__raw__={
        'sender._cls': PlayerTarget._class_name,
        'sender.player': document.minecraft_player.id,
        'sender.user': {'$ne': document.id}
    })
    for notification in sent_notifications:
        resolve_user(notification.sender)
        notification.save()  # MongoEngine takes care of dirty flags, it will only update if changed.

    received_notifications = BaseNotification.objects(__raw__={
        'receiver._cls': PlayerTarget._class_name,
        'receiver.player': document.minecraft_player.id,
        'receiver.user': {'$ne': document.id}
    })
    for notification in received_notifications:
        resolve_user(notification.sender)
        notification.save()  # MongoEngine takes care of dirty flags, it will only update if changed.
post_save.connect(handle_user_update, sender=User)


class PMNotification(BaseNotification):

    deletable = BooleanField(default=True)
    source = StringField()
    message = StringField(required=True)

    def render_notification_listing(self):
        return render_template('notification_list_entry_pm.html', notification=self)