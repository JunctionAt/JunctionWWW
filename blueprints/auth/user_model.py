from flask import url_for
from flask_login import current_user
from sqlalchemy import Column
from sqlalchemy.types import *

from blueprints.base import Base


class User(Base, object):

    __tablename__ = 'users'
    name = Column(String(16), primary_key=True)
    hash = Column(String(100))
    mail = Column(String(60))
    registered = Column(DateTime)
    verified = Column(Boolean)
