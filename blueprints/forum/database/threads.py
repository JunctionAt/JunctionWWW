from mongoengine import *

from posts import Post
from login import User

class Thread(Document):
    """
    A thread is a collection of Posts that make up the original post and the replies.
    """
    posts = ListField(ReferenceField(Post, dbref=False))
    author = ReferenceField(User, dbref=False)
    title = StringField()
    is_announcement = False
    topic_uuid = StringField()
    date = StringField()