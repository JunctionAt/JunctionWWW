import flask
import flask_login
from flask import render_template, request, current_app, abort, flash, redirect, url_for
import sqlalchemy
import sqlalchemy.orm
from sqlalchemy.orm import relation
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import *
from sqlalchemy import Column
from sqlalchemy.orm.exc import NoResultFound
from wtforms import Form, TextField, ValidationError
from wtforms.validators import Optional, Length
import re

from blueprints.base import Base
from blueprints.user_model import User
from blueprints.player_stats import player_stats


class Profile(Base, object):
    """The player profile table"""

    __tablename__ = 'player_profiles'
    name = Column(String(16), ForeignKey(User.name), primary_key=True)
    realname = Column(String(64))
    location = Column(String(64))
    tagline = Column(String(256))
    link = Column(String(256))
    show_stats = Column(String(64))
    default = False
    _user = relation(User, backref='profile', lazy=False)
    _stats = None

    @property
    def user(self):
        if not self._user:
            try:
                self._user = player_profiles.session.query(User).filter(User.name==self.name).one()
            except NoResultFound:
                self._user = Profile.default_user(self.name)
        return self._user

    @property
    def stats(self):
        if not self._stats:
            self._stats = dict([
                    (name, endpoint.get_by_name(self.name))
                    for name, endpoint in player_stats.endpoints.iteritems()
                    ])
        return self._stats

    @property
    def profile_stats(self):
        stats = filter(lambda (name, stats):
                           len(stats) and (not self.show_stats or name in self.show_stats),
                       self.stats.iteritems())
        if not len(stats): return None
        return dict(stats)

    @staticmethod
    def default_profile(name):
        """Return a default profile for unregistered users"""
        return Profile(
            name=name,
            show_stats=' '.join(player_stats.endpoints.keys()),
            default=True
        )
    
    @staticmethod
    def default_user(name):
        """Return a default user"""
        return User(name=name)



class Blueprint(flask.Blueprint, object):
    """Our blueprint that will lazy load it's session when in a flask context"""

    _session = None
    
    @property
    def session(self):
        if not self._session:
            self._session = sqlalchemy.orm.sessionmaker(current_app.config['ENGINE'])()
        return self._session

    @session.setter
    def session(self, session):
        return self._session
    
    def get_by_name(self, name):
        """Load a player profile for name, or the default profile.
        
        This is shorthand for (user.profile or player_profiles.default_profile())
        
        """
        try:
            return self.session.query(Profile).filter(Profile.name==name).one()
        except NoResultFound:
            return Profile.default_profile(name)

"""Singleton blueprint object"""
player_profiles = Blueprint('player_profiles', __name__, template_folder='templates')


# Blueprint routes

@player_profiles.route('/profile', methods=('GET', 'POST'))
@flask_login.login_required
def edit_profile():
    profile = player_profiles.get_by_name(flask_login.current_user.name)
    form = ProfileForm(request.form, profile)
    if request.method == 'POST' and form.validate():
        form.populate_obj(profile)
        profile.show_stats = ' '.join(re.compile('[,\s]+').split(profile.show_stats.lower()))
        player_profiles.session.add(profile)
        player_profiles.session.commit()
        flash('Profile saved')
        return redirect(url_for('player_profiles.edit_profile'))
    return render_template('edit_profile.html', form=form)

@player_profiles.route('/profile/<player>')
def show_profile(player):
    profile = player_profiles.get_by_name(player)
    # Error out if this the default profile is loaded and there are no stats
    if profile.default and not sum(map(lambda (_, stats): len(stats), profile.stats.items())):
        abort(404)
    return render_template('show_profile.html', profile=profile)

# Forms

class ProfileForm(Form):

    tagline = TextField('Tagline', [Optional(), Length(max=256)])
    realname = TextField('Real name', [Optional(),Length(max=64)])
    location = TextField('Location', [Optional(),Length(max=64)])
    link = TextField('Link', [Optional(),Length(max=256)])
    show_stats = TextField('Displayed stats', [Optional(),Length(max=64)])

    def validate_show_stats(self, field):
        invalid = list()
        parts = re.compile('[,\s]+').split(field.data.lower())
        servers = player_stats.endpoints.keys()
        for server in parts:
            if not server in servers:
                invalid.append(server)
        if len(invalid):
            raise ValidationError('Invalid servers: %s'%', '.join(invalid))

