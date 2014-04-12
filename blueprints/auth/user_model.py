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


class PlayerUUIDName(EmbeddedDocument):
    mcname = StringField(required=True, min_length=3, max_length=16)

    start_date = DateTimeField(required=True, default=datetime.datetime.utcnow)
    end_date = DateTimeField(required=True, default=datetime.datetime.utcnow)


class PlayerUUID(EmbeddedDocument):

    uuid = UUIDField(required=True, unique=True, binary=False)
    mcname = StringField(required=True, min_length=3, max_length=16)

    seen_mcnames = ListField(EmbeddedDocumentField(PlayerUUIDName))

    def find_seen_mcname(self, mcname):
        """
        Searches all seen mcnames for all occurrences of the provided username.
        :param mcname:
        :return: A ordered (newest first) list of PlayerUUIDName objects representing the seen mcnames and its date
        ranges.
        """
        mcnames = list()
        for seen_mcname in self.seen_mcnames:
            if seen_mcname.mcname == mcname:
                mcnames.append(seen_mcname)
        mcnames.sort(key=lambda x: x.start_date, reverse=True)
        return mcnames

    def checkin_mcname(self, mcname):
        """
        Updates the UUID with the provided username. This should normally only be called on server login.
        :param mcname: Ingame username
        """
        if self.mcname is not None and mcname.lower() == self.mcname.lower():  # If the name is already current...
            mcname_obj = self.find_seen_mcname(mcname)[0]
            mcname_obj.end_date = datetime.datetime.utcnow()  # update last seen...
            mcname_obj.mcname = mcname  # and username casing.
        else:  # Else if the username isn't current...
            self.mcname = mcname  # set current username...
            mcname_obj = PlayerUUIDName()
            mcname_obj.mcname = mcname
            self.seen_mcnames.append(mcname_obj)  # and add a new history object.


class User(Document, flask_login.UserMixin, object):

    name = StringField(required=True, unique=True)
    # noinspection PyShadowingBuiltins
    hash = StringField(required=True)

    minecraft_user = EmbeddedDocumentField(PlayerUUID)

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
