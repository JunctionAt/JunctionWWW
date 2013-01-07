__author__ = 'HansiHE'

from mongoengine import *

class Role_Group(Document):

    name = StringField(required=True)
    roles = ListField(StringField())

    meta = {
        'collection': 'role_groups'
    }