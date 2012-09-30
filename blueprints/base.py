import flask
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

Base = declarative_base()
Base.metadata.bind = flask.current_app.config['ENGINE']

session = scoped_session(sessionmaker(flask.current_app.config['ENGINE']))

@flask.current_app.after_request
def remove(response):
    session.remove()
    return response
