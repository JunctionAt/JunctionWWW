from mongoengine import *

from categories import Category

class Forum(Document):
    """
    This represents the entire forum.
    This class keeps a reference of all the categories.
    """
    name = StringField()
    categories = ListField(ReferenceField(Category, dbref=False))