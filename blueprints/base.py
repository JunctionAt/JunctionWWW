from flask import current_app
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
Base.metadata.bind = current_app.config['ENGINE']
