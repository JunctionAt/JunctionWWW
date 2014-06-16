import flask_login
from mongoengine import *
from flask import url_for
from datetime import datetime
import re
from permissions import PermissionHolderMixin
from util import method_once


class Role_Group(Document):

    name = StringField(required=True)
    roles = ListField(StringField())

    meta = {
        'collection': 'role_groups',
        'indexed': ['name', 'roles']
    }

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class User(Document, flask_login.UserMixin, PermissionHolderMixin, object):

    name = StringField(required=True, unique=True)
    # noinspection PyShadowingBuiltins
    hash = StringField(required=True)

    tfa = BooleanField(default=False)
    tfa_method = StringField()
    tfa_secret = StringField()
    tfa_info = DictField()

    # If this ever changes so that each user may have multiple minecraft accounts, update notifications_model as well.
    minecraft_player = ReferenceField("MinecraftPlayer", db_field="minecraft_player", dbref=False, required=True)

    mail = StringField()
    mail_verified = BooleanField(default=False)

    reddit_username = StringField()

    registered = DateTimeField(default=datetime.utcnow, required=True)

    # Note for whoever: Most permissions should be added through groups, not adding nodes directly to users.
    # The permissions list should ONLY be used in very specific cases. (Api accounts?)
    # TODO: Refactor permissions into some PermissionHolder class. It can be used by both the User and ApiKey model.
    role_groups = ListField(ReferenceField(Role_Group, dbref=False))
    roles = ListField(StringField())

    meta = {
        'collection': 'users',
        'indexed': ['name', 'minecraft_player']
    }

    def validate(self, clean=True):
        if not validate_username(self.name):
            raise ValidationError("Username could not be validated.")

        return super(User, self).validate(clean)

    def get_id(self):
        return self.name

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    # User is fetched from db on each request. Caching it on a per-instance basis should be fine.
    @method_once
    def get_permissions(self):
        permissions = list()

        # Add all permissions set on the user document.
        for role in self.roles:
            permissions.append(role)

        # Add all permissions from all the role_groups the user has.
        for group in self.role_groups:
            for role in group.roles:
                permissions.append(role)

        return permissions

    def get_profile_url(self):
        return url_for('player_profiles.profile_view', name=self.name)

    def get_avatar_url(self):
        return url_for('avatar.get_avatar', name=self.name)

    def is_player(self, player):
        """
        Checks if the supplied MinecraftPlayer is associated with this User.
        :param player:
        :return:
        """
        return player == self.minecraft_player

    @classmethod
    def get_user_by_uuid(cls, uuid):
        """
        You can pass this either a string UUID or a MinecraftPlayer document instance. It will return the user
        owning the Minecraft account. Keep in mind that not every player is registered in our database, and
        this may very well return None.
        """
        return User.objects(minecraft_player=uuid).first()

    @classmethod
    def get_user_by_name(cls, name):
        """
        This takes a junction username, and returns the User document with that name. Returns null if no
        user has this username.
        """
        return User.objects(name__iexact=name).first()


class ConfirmedUsername(Document):

    username = StringField(required=True)
    ip = StringField(required=True)
    uuid = UUIDField(required=True)

    created = DateTimeField(required=True, default=datetime.utcnow)


def validate_username(username):
    if 2 <= len(username) <= 16 and re.match(r'^[A-Za-z0-9_]+$', username):
        return True
    return False
