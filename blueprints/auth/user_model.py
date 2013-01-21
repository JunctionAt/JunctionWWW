import flask_login
import datetime

from mongoengine import *

class Role_Group(Document):

    name = StringField(required=True)
    roles = ListField(StringField())

    meta = {
        'collection': 'role_groups',
        'indexes': ['roles']
    }

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

class User(Document, flask_login.UserMixin, object):

    name = StringField(required=True, unique=True)
    hash = StringField(required=True)
    mail = StringField()
    registered = DateTimeField(default=datetime.datetime.utcnow())
    verified = BooleanField(default=False)

    notifications = ListField(ReferenceField('Notification', dbref=False))

    #Note for whoever: Most permissions should be added through groups, not adding nodes directly to users.
    #The permissions list should ONLY be used in very specific cases. (Api accounts?)
    role_groups = ListField(ReferenceField(Role_Group, dbref=False))
    roles = ListField(StringField())

    api_account = BooleanField(default=False)

    meta = {
        'collection': 'users',
        'indexes': ['name']
    }

    def get_id(self):
        return self.name

    def __repr__(self):
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

class Token(Document):

    token = StringField(required=True)
    name = StringField(primary_key=True, required=True)
    hash = StringField(required=True)
    mail = StringField()
    ip = StringField(required=True)
    expires = DateTimeField(required=True)

    meta = {
        'collection': 'tokens'
    }

#from blueprints.base import Base, session, db
#
#class User(Base, flask_login.UserMixin, object):
#
#    __tablename__ = 'users'
#    name = db.Column(db.String(16), primary_key=True)
#    hash = db.Column(db.String(100))
#    mail = db.Column(db.String(60))
#    registered = db.Column(db.DateTime, default=datetime.datetime.utcnow)
#    verified = db.Column(db.Boolean)
#
#    def get_id(self):
#        return self.name
#
#    def __repr__(self):
#        return self.name
#
#class Token(Base):
#
#    __tablename__ = 'tokens'
#    token = db.Column(db.CHAR(6), primary_key=True)
#    name = db.Column(db.String(16), db.ForeignKey(User.name), index=True)
#    hash = db.Column(db.String(100), index=True)
#    mail = db.Column(db.String(60))
#    ip = db.Column(db.String(39))
#    expires = db.Column(db.TIMESTAMP(), default=datetime.datetime.utcnow)
#    user = db.relation(User, backref='tokens')