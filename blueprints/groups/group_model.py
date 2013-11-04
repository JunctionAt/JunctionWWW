__author__ = 'HansiHE'

from mongoengine import Document, EmbeddedDocument, StringField, ListField, ReferenceField
from blueprints.auth.user_model import User


class GroupMember(EmbeddedDocument):

    user = ReferenceField(User, dbref=False)

    access = StringField(choices=['member', 'manager', 'owner'], default='member')


class GroupModel(Document):

    name = StringField()
    description = StringField()

    members = ListField(ReferenceField(User))
