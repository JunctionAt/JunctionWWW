from flask import current_app
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.cache import Cache
from mongoengine import connect
from flask.ext.admin import Admin

db = SQLAlchemy(current_app)
session = db.session
Base = db.Model

cache = Cache(current_app, config={'CACHE_TYPE': 'simple'})

mongo = connect("pf")

admin = Admin(current_app)