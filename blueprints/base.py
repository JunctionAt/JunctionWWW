import flask
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

Base = declarative_base()
Base.metadata.bind = flask.current_app.config['ENGINE']

class Session:
    
    def __init__(self):
        self.Session = scoped_session(sessionmaker(flask.current_app.config['ENGINE']))

    @flask.current_app.after_request
    def remove(response):
        session.Session.remove()
        return response

    def execute(self, *args, **kwargs):
        return self.Session.execute(*args, **kwargs)

    def query(self, *args, **kwargs):
        return self.Session.query(*args, **kwargs)
    

session = Session()
