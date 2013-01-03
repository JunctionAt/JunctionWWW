from mongoengine import *
from threads import Thread

class Board(Document):
    """
    A Board object represents a list of topics.
    """
    name = StringField()
    board_id = SequenceField(unique=True)
    description = StringField()
    topics = ListField(ReferenceField(Thread, dbref=False))