__author__ = 'HansiHE'

from mongoengine import Document, ListField, EmbeddedDocumentField, EmbeddedDocument, StringField, DateTimeField, ValidationError
from datetime import datetime


class ServerRevision(EmbeddedDocument):
    name = StringField(required=True)
    description = StringField()

    rev_id = StringField(required=True, regex=r'^[^:]+$')  # Not containing colons

    start_date = DateTimeField(required=True, default=datetime.utcnow)
    end_date = DateTimeField(default=None)

    @property
    def fid(self):
        return self.server.server_id + ":" + self.rev_id

    def is_active(self):
        if self.end_date and self.end_date < datetime.utcnow():
            return False
        return True


class Server(Document):
    name = StringField(required=True)
    description = StringField()

    server_id = StringField(required=True, unique=True, regex=r'^[^:]+$')  # Not containing colons

    revisions = ListField(EmbeddedDocumentField(ServerRevision), required=True)

    @classmethod
    def get_server(cls, fid):
        return cls.objects(server_id=fid.split(":")[0]).first()

    @classmethod
    def get_server_revision(cls, fid):
        return cls.get_server(fid).get_revision(fid)

    def get_revision(self, fid):
        rev_id = fid.split(":")[1]
        for revision in self.revisions:
            if revision.rev_id == rev_id:
                revision.server = self
                return revision
        return None

    def validate(self, *args, **kwargs):
        super(Server, self).validate(*args, **kwargs)

        rev_ids = []
        for revision in self.revisions:
            if revision.rev_id in rev_ids:
                raise ValidationError("Duplicate revision id in Server db document")
            rev_ids += revision.rev_id