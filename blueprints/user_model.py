from sqlalchemy import Column
from sqlalchemy.types import *
from blueprints.base import Base
import md5

class User(Base, object):
    __tablename__ = 'users'
    name = Column(String(16), primary_key=True)
    hash = Column(String(100))
    mail = Column(String(60))
    registered = Column(DateTime)
    verified = Column(Boolean)

    @property
    def avatar(self):
        if not self.mail: return None
        base = "http://www.gravatar.com/avatar/%s.png"%md5.new(self.mail).hexdigest().lower()
        return type('Avatar', (object, ), {
                "small": "%s?s=32"%base,
                "medium": "%s?s=64"%base,
                "large": "%s?s=128"%base,
                "portrait": "%s?s=256"%base
                })
