from flask import Flask
from blueprints.base import Base, session, db
import datetime

class Ban(db.Model):
    __tablename__ = 'bans_bans'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    issuer = db.Column(db.String(20))
    username = db.Column(db.String(20))
    reason = db.Column(db.String(500))
    server = db.Column(db.String(100))
    time = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__ (self, issuer, username, reason, server):
        self.issuer = issuer
        self.username = username
        self.reason = reason
        self.server = server

    def gettime(self):
        return self.time.strftime("%s")

    def __repr__(self):
        return self.id

class RemovedBan(db.Model):
    __tablename__ = 'bans_removedbans'

    id = db.Column(db.Integer, primary_key=True)
    issuer = db.Column(db.String(20))
    username = db.Column(db.String(20))
    reason = db.Column(db.String(500))
    server = db.Column(db.String(100))
    remover = db.Column(db.String(20))
    timeadded = db.Column(db.DateTime)
    timeremoved = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, ban, deletedby):
        self.id = ban.id
        self.issuer = ban.issuer
        self.username = ban.username
        self.reason = ban.reason
        self.server = ban.server
        self.remover = deletedby
        self.timeadded = ban.time

    def getaddedtime(self):
        return self.timeadded.strftime("%s")

    def getremovedtime(self):
        return self.timeremoved.strftime("%s")

    def __repr__(self):
        return self.id

class Note(db.Model):
    __tablename__ = 'bans_notes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    issuer = db.Column(db.String(20))
    username = db.Column(db.String(20))
    note = db.Column(db.String(500))
    server = db.Column(db.String(100))
    time = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__ (self, issuer, username, note, server):
        self.issuer = issuer
        self.username = username
        self.note = note
        self.server = server

    def gettime (self):
        return self.time.strftime("%s")

    def __repr__ (self):
        return self.id

class RemovedNote(db.Model):
    __tablename__ = 'bans_removednote'

    id = db.Column(db.Integer, primary_key=True)
    issuer = db.Column(db.String(20))
    username = db.Column(db.String(20))
    note = db.Column(db.String(500))
    server = db.Column(db.String(100))
    remover = db.Column(db.String(20))
    timeadded = db.Column(db.DateTime)
    timeremoved = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, note, deletedby):
        self.id = note.id
        self.issuer = note.issuer
        self.username = note.username
        self.note = note.note
        self.server = note.server
        self.remover = deletedby
        self.timeadded = note.time

    def getaddedtime(self):
        return self.timeadded.strftime("%s")

    def getremovedtime(self):
        return self.timeremoved.strftime("%s")

    def __repr__(self):
        return self.id
