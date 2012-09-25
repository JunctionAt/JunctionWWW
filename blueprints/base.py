import flask
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Blueprint(flask.Blueprint):

    def register(self, *args):
        """Overridden method that will be passed the app as args[0].

        Then we bind the DB to the common base!

        """
        
        Base.metadata.bind = args[0].config['ENGINE']
        super(Blueprint, self).register(*args)
        
base = Blueprint('base', __name__)
