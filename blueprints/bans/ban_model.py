from flask import Flask
from blueprints.base import Base, session, db
import datetime

class Ban(db.Model):
    __tablename__ = 'bans'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    issuer = db.Column(db.String(20))
    banned = db.Column(db.String(20))
    reason = db.Column(db.String(500))
    server = db.Column(db.String(100))
    time = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__ (self, issuer, banned, reason, server):
        self.issuer = issuer
        self.banned = banned
        self.reason = reason
        self.server = server

    def gettime(self):
        return self.time.strftime("%s")

    def __repr__(self):
        return self.id
