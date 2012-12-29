from flask import current_app
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.cache import Cache

db = SQLAlchemy(current_app)
session = db.session
Base = db.Model
cache = Cache(current_app, config={'CACHE_TYPE': 'simple'})