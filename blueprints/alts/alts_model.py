__author__ = 'HansiHE'

import mongoengine
import datetime


class PlayerIpsModel(mongoengine.Document):

    username = mongoengine.StringField(required=True, unique=True)
    ips = mongoengine.ListField(mongoengine.StringField(), required=True)

    last_login = mongoengine.DateTimeField(required=True)

    def update_last_login(self):
        self.last_login = datetime.datetime.utcnow()

    meta = {
        'collection': 'player_ip_relationships',
        'indexed': ['username', 'ips']
    }


class IpPlayersModel(mongoengine.Document):

    ip = mongoengine.StringField(required=True, unique=True)
    usernames = mongoengine.ListField(mongoengine.StringField(), required=True)

    last_login = mongoengine.DateTimeField(required=True)

    def update_last_login(self):
        self.last_login = datetime.datetime.utcnow()

    meta = {
        'collection': 'ip_player_relationships',
        'indexed': ['ip', 'usernames']
    }