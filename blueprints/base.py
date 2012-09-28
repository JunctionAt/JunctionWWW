from flask import current_app
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
Base.metadata.bind = current_app.config['ENGINE']
session = sessionmaker(current_app.config['ENGINE'])()
