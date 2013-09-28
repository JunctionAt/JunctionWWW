__author__ = 'HansiHE'

from mongoengine import Document, UUIDField, StringField, ReferenceField, BooleanField, ListField
from uuid import uuid4
from blueprints.auth.user_model import User


class ApiKey(Document):

    key = UUIDField(binary=False, required=True, default=uuid4, unique=True)
    owner = ReferenceField(User, required=True)

    write = BooleanField(default=False)
    as_user = BooleanField(default=False)

    access = ListField(StringField())

    label = StringField(max_length=20)