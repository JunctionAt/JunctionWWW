from flask import current_app
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy(current_app)
session = db.session
Base = db.Model
