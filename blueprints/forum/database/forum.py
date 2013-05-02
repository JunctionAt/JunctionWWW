from mongoengine import *

from blueprints.auth.user_model import User
from datetime import datetime
from flask import url_for


class Forum(Document):
    name = StringField()
    identifier = StringField(unique=True)

    meta = {
        'collection': 'forum_forums',
        'indexes': ['identifier']
    }

    def get_url(self):
        return url_for('forum.view_forum', forum=self.identifier)


class Category(Document):
    name = StringField()
    description = StringField()

    order = IntField()

    forum = ReferenceField(Forum, dbref=False)

    meta = {
        'collection': 'forum_categories',
        'indexes': ['forum']
    }

    def get_boards(self):
        return Board.objects(categories__in=[self])


class Board(Document):
    name = StringField()
    board_id = SequenceField(unique=True)
    description = StringField()

    categories = ListField(ReferenceField(Category, dbref=False))
    forum = ReferenceField(Forum, dbref=False)

    meta = {
        'collection': 'forum_boards',
        'indexes': ['forum', 'categories', 'board_id']
    }

    def get_topic_count(self):
        return len(Topic.objects(forum=self))

    def get_url_name(self):
        return self.name.replace(' ', '_')

    def get_url_info(self):
        return {'board_id': self.board_id, 'board_name': self.get_url_name()}

    def get_url(self):
        return url_for('forum.view_board', **self.get_url_info())

    def get_post_url(self):
        return url_for('forum.post_topic', **self.get_url_info())


class TopicEdit(EmbeddedDocument):

    author = ReferenceField(User, dbref=False)
    title = StringField()
    date = DateTimeField()
    announcement = BooleanField(default=False)


class Topic(Document):
    title = StringField()

    author = ReferenceField(User, dbref=False)
    date = DateTimeField(default=datetime.utcnow, required=True)
    announcement = BooleanField(default=False)

    topic_url_id = SequenceField(unique=True)

    last_editor = ReferenceField(User, dbref=False)
    edits = ListField(EmbeddedDocumentField(TopicEdit))

    board = ReferenceField(Board, dbref=False)
    forum = ReferenceField(Forum, dbref=False)

    meta = {
        'collection': 'forum_topics',
        'indexes': ['board', 'author', 'topic_url_id']
    }

    def get_url_name(self):
        return pretty_url_escape(self.title)

    def get_url_info(self):
        return {'topic_id': self.topic_url_id, 'topic_name': self.get_url_name()}

    def get_url(self):
        return url_for('forum.view_topic', **self.get_url_info())


class PostEdit(EmbeddedDocument):
    author = ReferenceField(User, dbref=False)
    content = StringField()
    date = DateTimeField()


class Post(Document):
    author = ReferenceField(User, dbref=False)
    content = StringField()
    date = DateTimeField(default=datetime.utcnow, required=True)  # JESUS THIS GETS ME EVERY TIME

    edits = ListField(EmbeddedDocumentField(PostEdit))

    topic = ReferenceField(Topic, dbref=False)
    forum = ReferenceField(Forum, dbref=False)

    meta = {
        'collection': 'forum_posts',
        'indexes': ['topic', 'author']
    }


def pretty_url_escape(string):
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 "
    return ''.join([s for s in string if s in chars]).replace(" ", "_")