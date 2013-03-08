__author__ = 'HansiHE'

from mongoengine import *

class Avatar(Document):

    username = StringField(primary_key=True, required=True)
    image = ImageField(size=(128, 128, True), thumbnail_size=(32, 32, True))

    #Source: 0=default, 1=minecraft head, 2=custom upload
    #source = IntField(default=0)

    meta = {
        'collection': 'avatars',
        'indexed' : [ 'username' ]
    }