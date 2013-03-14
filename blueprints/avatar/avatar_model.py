__author__ = 'HansiHE'

from mongoengine import *
from datetime import datetime

class Avatar(Document):

    username = StringField(primary_key=True, required=True)
    image = ImageField(size=(128, 128, True), thumbnail_size=(32, 32, True))
    last_modified = DateTimeField(default=datetime.utcnow, required=True)

    #Source: 0=default, 1=minecraft head, 2=custom upload
    #source = IntField(default=0)

    meta = {
        'collection': 'avatars',
        'indexed' : [ 'username' ]
    }