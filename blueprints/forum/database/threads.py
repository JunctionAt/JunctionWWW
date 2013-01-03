from mongoengine import *

from posts import Post
from login import User

class Thread(Document):
    """
    A thread is a collection of Posts that make up the original post and the replies.
    """
    posts = ListField(ReferenceField(Post, dbref=False))
    author = StringField()
    title = StringField()
    is_announcement = False
    topic_url_id = SequenceField(unique=True)
    topic_url_name = StringField()
    date = StringField()