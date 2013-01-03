__author__ = 'HansiHE'

from mongoengine import *

class Counter(Document):

    name = StringField(unique=True)
    incremental = SequenceField()
