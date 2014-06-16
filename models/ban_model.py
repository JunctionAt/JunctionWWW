from flask.templating import render_template
from mongoengine import *
import datetime
import mongoengine
from models.notification_model import BaseNotification, PlayerTarget, UserTarget, StaticTarget
from models.player_model import MinecraftPlayer

from .user_model import User
from .servers_model import Server


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

    # 0:open - 1:hard closed for timeframe - 2:hard closed forever
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

    watching = ListField(ReferenceField('User'))

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

    def ban_lifted(self):
        BanNotification.send_notifications(self, "unbanned")

    def get_time(self):
        return self.time.strftime("%s")

    def get_server(self):
        return Server.get_server(self.server)

    def get_revision(self):
        return self.get_server().get_revision(self.server)

    def __repr__(self):
        return self.id

    def __str__(self):
        return 'Ban #{0}'.format(self.uid)

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

    def get_time(self):
        return self.time.strftime("%s")

    def __repr__(self):
        return self.id

    meta = {
        'collection': 'notes',
        'indexed': ['uid', 'issuer', 'username']
    }


class BanNotification(BaseNotification):
    ban = ReferenceField(Ban, required=True)
    action = StringField(choices=["banned", "reply", "unbanned"], required=True)

    def render_notification_listing(self):
        name = self.ban.target.mcname

        if self.action == "banned":
            text = "{0} has been banned.".format(name)
        elif self.action == "reply":
            text = "Someone replied to {0}'s ban.".format(name)
        elif self.action == "unbanned":
            text = "{0} has been unbanned.".format(name)
        else:
            text = "Something has changed in {0}'s ban.".format(name)

        return render_template('notification_list_entry_ban.html', notification=self, text=text)

    @classmethod
    def send(cls, ban, target, action):
        if isinstance(target, User):
            receiver = UserTarget(user=target)
        elif isinstance(target, MinecraftPlayer):
            receiver = PlayerTarget(player=target).with_user()
        else:
            raise TypeError()

        notification = BanNotification(receiver=receiver, sender=StaticTarget(identifier="ban"), ban=ban, action=action)
        notification.save()
        return notification

    @classmethod
    def send_notifications(cls, ban, action):
        cls.send(ban, ban.target, action)
        for watcher in ban.watching:
            cls.send(ban, watcher, action)


def ban_creation_notification(sender, document, created=False):
    if created:
        BanNotification.send_notifications(document, "banned")
mongoengine.signals.post_save.connect(ban_creation_notification, sender=Ban)