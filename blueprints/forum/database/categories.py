from mongoengine import *
from boards import Board

class Category(Document):
    """
    A category object represents a list of boards.
    """
    name = StringField()
    description = StringField()
    boards = ListField(ReferenceField(Board, dbref=False))