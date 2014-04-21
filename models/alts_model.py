__author__ = 'HansiHE'

import mongoengine
import datetime


class PlayerIpsModel(mongoengine.Document):

    player = mongoengine.ReferenceField('MinecraftPlayer', dbref=False, required=True)
    ips = mongoengine.ListField(mongoengine.StringField(), required=True)

    last_login = mongoengine.DateTimeField(required=True, default=datetime.datetime.utcnow())

    def update_last_login(self):
        self.update(set__last_login=datetime.datetime.utcnow())

    def update_last_login_and_add_entry(self, entry):
        self.update(set__last_login=datetime.datetime.utcnow(), add_to_set__ips=entry)

    meta = {
        'collection': 'player_ip_relationships',
        'indexed': ['username', 'ips']
    }


class IpPlayersModel(mongoengine.Document):

    ip = mongoengine.StringField(required=True, unique=True)
    players = mongoengine.ListField(mongoengine.ReferenceField('MinecraftPlayer', dbref=False), required=True)

    last_login = mongoengine.DateTimeField(required=True, default=datetime.datetime.utcnow())

    def update_last_login(self):
        self.update(set__last_login=datetime.datetime.utcnow())

    def update_last_login_and_add_entry(self, entry):
        self.update(set__last_login=datetime.datetime.utcnow(), add_to_set__players=entry)

    meta = {
        'collection': 'ip_player_relationships',
        'indexed': ['ip', 'usernames']
    }