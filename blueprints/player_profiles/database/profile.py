__author__ = 'HansiHE'

from mongoengine import *
from flask import url_for


class PlayerProfile(Document):

    user = ReferenceField('User', dbref=False)

    profile_text = StringField(default="I play minecraft :D")

    badges = ListField(StringField())

    def get_edit_text_url(self):
        return url_for('player_profiles.profile_text_edit', name=self.user.name)

    def get_profile_url(self):
        return url_for('player_profiles.profile_view', name=self.user.name)

    def get_send_pm_url(self):
        return url_for('player_profiles.send_pm', name=self.user.name)
