__author__ = 'HansiHE'

from mongoengine import *

class PlayerAlt(Document):

    username = StringField(required=True, unique=True)

    ips = ListField(StringField(), required=True)

    meta = {
        'collection' : 'alts',
        'indexed' : [ 'username', 'ips' ]
    }

