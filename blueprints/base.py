import flask
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
Base.metadata.bind = flask.current_app.config['ENGINE']

class Session:
    
    session = property(lambda self: self._session if self._session else self.create())
    _session = None
    
    def __init__(self):
        self.sessionmaker = sessionmaker(flask.current_app.config['ENGINE'])

    def create(self):
        self._session = self.sessionmaker()
        return self._session
                       

    @flask.current_app.after_request
    def close(response):
        if session._session:
            session._session.close()
            session._session = None
        return response

    def execute(self, *args, **kwargs):
        return self.session.execute(*args, **kwargs)

    def query(self, *args, **kwargs):
        return self.session.query(*args, **kwargs)
    

session = Session()
