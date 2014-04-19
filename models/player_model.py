__author__ = 'hansihe'

from mongoengine import Document, UUIDField, StringField, EmbeddedDocument, EmbeddedDocumentField, DateTimeField, ListField, BooleanField
import datetime


class PlayerName(EmbeddedDocument):
    mcname = StringField(required=True, min_length=3, max_length=16)

    before_uuid_update = BooleanField(default=False)

    start_date = DateTimeField(required=True, default=datetime.datetime.utcnow)
    end_date = DateTimeField(required=True, default=datetime.datetime.utcnow)


class MinecraftPlayer(Document):
    """

    """
    uuid = UUIDField(binary=False, primary_key=True, unique=True, required=True)
    mcname = StringField(min_length=3, max_length=16, required=True)

    seen_mcnames = ListField(EmbeddedDocumentField(PlayerName))

    def find_seen_mcname(self, mcname):
        """
        Searches all seen mcnames for all occurrences of the provided username.
        :param mcname:
        :return: A ordered (newest first) list of PlayerUUIDName objects representing the seen mcnames and its date
        ranges.
        """
        mcnames = list()
        for seen_mcname in self.seen_mcnames:
            if seen_mcname.mcname.lower() == mcname.lower():
                mcnames.append(seen_mcname)
        mcnames.sort(key=lambda x: x.start_date, reverse=True)
        return mcnames

    def checkin_mcname(self, mcname):
        """
        Updates the UUID with the provided username. This should normally only be called on server login.
        :param mcname: Ingame username
        """
        if self.mcname is not None and mcname.lower() == self.mcname.lower():  # If the name is already current...
            mcname_obj = self.find_seen_mcname(mcname)[0]
            mcname_obj.end_date = datetime.datetime.utcnow()  # update last seen...
            mcname_obj.mcname = mcname  # and username casing.
        else:  # Else if the username isn't current...
            self.mcname = mcname  # set current username...
            mcname_obj = PlayerName()
            mcname_obj.mcname = mcname
            self.seen_mcnames.append(mcname_obj)  # and add a new history object.

    @classmethod
    def find_or_create_player(cls, uuid, mcname):
        player = MinecraftPlayer.find_player(uuid)
        if not player:
            player = MinecraftPlayer(uuid=uuid)

        player.checkin_mcname(mcname)

        player.save()

        return player

    @classmethod
    def find_player(cls, uuid):
        return MinecraftPlayer.objects(uuid=uuid).first()