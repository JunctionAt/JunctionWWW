import flask_login
import datetime

from mongoengine import *
from flask import url_for


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


class User(Document, flask_login.UserMixin, object):

    name = StringField(required=True, unique=True)
    # noinspection PyShadowingBuiltins
    hash = StringField(required=True)

    mail = StringField()
    mail_verified = BooleanField(default=False)

    reddit_username = StringField()

    registered = DateTimeField(default=datetime.datetime.utcnow, required=True)

    #Not currently used
    #notifications = ListField(ReferenceField('Notification', dbref=False))

    #Note for whoever: Most permissions should be added through groups, not adding nodes directly to users.
    #The permissions list should ONLY be used in very specific cases. (Api accounts?)
    role_groups = ListField(ReferenceField(Role_Group, dbref=False))
    roles = ListField(StringField())

    api_account = BooleanField(default=False)

    meta = {
        'collection': 'users',
        'indexed': ['name']
    }

    def get_id(self):
        return self.name

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    permissions = []

    def load_perms(self):
        self.permissions = []
        for role in self.roles:
            self.permissions.append(role)
        for group in self.role_groups:
            for role in group.roles:
                self.permissions.append(role)

    def has_permission(self, perm_node):
        node = unicode(perm_node)
        #print node
        for permission in self.permissions:
            if permission.startswith(u"-"):
                if permission.endswith(u"*"):
                    if node.startswith(permission[1:-1]):
                        return False
                else:
                    if permission[1:] == node:
                        return False

        for permission in self.permissions:
            if permission.endswith(u"*"):
                if node.startswith(permission[:-1]):
                    return True
            else:
                if permission == node:
                    return True

        return False

    def get_profile_url(self):
        return url_for('player_profiles.profile_view', name=self.name)

    def get_avatar_url(self):
        return url_for('avatar.get_avatar', name=self.name)


#class Token(Document):
#
#    token = StringField(required=True)
#    name = StringField(required=True)
#    # noinspection PyShadowingBuiltins
#    hash = StringField(required=True)
#    mail = StringField()
#    ip = StringField(required=True)
#    expires = DateTimeField(required=True)
#
#    meta = {
#        'collection': 'tokens'
#    }


class ConfirmedUsername(Document):

    username = StringField(required=True)
    ip = StringField(required=True)
    created = DateTimeField(required=True, default=datetime.datetime.utcnow)
