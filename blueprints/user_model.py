from flask import url_for
from sqlalchemy import Column
from sqlalchemy.types import *
from blueprints.base import Base
import md5
import urllib

class User(Base, object):
    __tablename__ = 'users'
    name = Column(String(16), primary_key=True)
    hash = Column(String(100))
    mail = Column(String(60))
    registered = Column(DateTime)
    verified = Column(Boolean)

    @property
    def avatar(self):
        mail = self.mail or ""
        hash = md5.new(mail).hexdigest().lower()
        link = "http://www.gravatar.com/%s"%hash if self.mail else None
        img = "http://www.gravatar.com/avatar/%s.png?r=pg&d=%s"% \
            (hash, urllib.quote(url_for('static_pages.static',
                                        filename='default_avatar.png',
                                        _external=True)))
        return type('Avatar', (object, ), {
                "link": link,
                "small": "%s&s=32"%img,
                "medium": "%s&s=64"%img,
                "large": "%s&s=128"%img,
                "portrait": "%s&s=256"%img
                })
