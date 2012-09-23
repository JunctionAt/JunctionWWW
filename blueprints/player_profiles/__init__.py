import flask
from flask import render_template, current_app, abort
import sqlalchemy
import sqlalchemy.orm
from sqlalchemy.orm import relation
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import *
from sqlalchemy import Column
from sqlalchemy.orm.exc import NoResultFound
import flask_login
import md5
from blueprints.base import Base
from blueprints.user_model import User
from blueprints.player_stats import player_stats

class Profile(Base, object):
    """The player profile table"""

    __tablename__ = 'player_profiles'
    name = Column(String(16), ForeignKey(User.name), primary_key=True)
    realname = Column(String(64))
    location = Column(String(32))
    tagline = Column(String(140))
    link = Column(String(256))
    show_stats = Column(String(64))
    user = relation(User)

    @property
    def avatar(self):
        if not self.user.mail: return None
        return "http://www.gravatar.com/avatar/%s"%md5.new(self.user.mail).digest()

    @property
    def stats(self):
        return dict([
                (name, endpoint.get_by_name(self.name))
                for name, endpoint in player_stats.endpoints.iteritems()
                ])

    @property
    def profile_stats(self):
        return dict(filter(lambda (name, stats):
                               len(stats) and (not self.show_stats or name in self.show_stats),
                           self.stats.iteritems()))


def default_profile(name):
    """Return an empty profile"""
    return Profile(
        name=name,
        show_stats=' '.join(player_stats.endpoints.keys()),
        )

class Blueprint(flask.Blueprint, object):
    """Our blueprint that will lazy load when it's in a flask context"""

    _session = None
    
    @property
    def session(self):
        if not self._session:
            self._session = sqlalchemy.orm.create_session(current_app.config['ENGINE'])
        return self._session

    @session.setter
    def session(self, session):
        return self._session

    def get_by_name(self, name):
        """Load a player profile for name"""
        try:
            return self.session.query(Profile).filter(Profile.name==name).one()
        except NoResultFound:
            return default_profile(name)


"""Singleton blueprint object"""
player_profiles = Blueprint('player_profiles', __name__,
                            template_folder='templates',
                            static_folder='static',
                            static_url_path='/player_profiles/static')


# Blueprint routes

@player_profiles.route('/profile')
@flask_login.login_required
def edit_profile():
    return render_template('edit_profile.html',
                           profile=player_profiles.get_by_name(flask_login.current_user.name))

@player_profiles.route('/profile/<player>')
def show_profile(player):
    return render_template('show_profile.html',
                           profile=player_profiles.get_by_name(player))


# Blueprint helpers

