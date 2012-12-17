from mongoengine import *

from login import User

class Post(Document):
    """
    A post is the last object in the big list of referenced fields.
    It works like this,
    one Board has many Categories
    one Category has many topics (threads)
    one Thread has many Posts
    one Post has one User
    """
    author = ReferenceField(User, dbref=False)
    content = StringField()
    date = StringField()