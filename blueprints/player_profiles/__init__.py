import flask
import flask_login
from flask import render_template, request, current_app, abort, flash, redirect, url_for
import sqlalchemy
import sqlalchemy.orm
from sqlalchemy.orm import relation, backref
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import *
from sqlalchemy import Column
from sqlalchemy.orm.exc import NoResultFound
from wtalchemy.orm import model_form
from wtforms.validators import Optional, Length, ValidationError
import re

from blueprints.base import Base
from blueprints.auth.user_model import User
from blueprints.player_stats import player_stats
from blueprints.avatar import avatar


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
    _user = relation(User, backref=backref('_profile', uselist=False), lazy=False)
    _stats = None

    @property
    def user(self):
        """Return the user associated with this profile.
        
        This property will first see if the user was autoloaded, which will occur if there
        was a profile in the db.  If there wasn't a profile, if will get the user from db
        based off self.name.  If there was no registered user in the db, then, provide a
        user object with default attributes.

        """
        if not self._user:
            try:
                self._user = player_profiles.session.query(User) \
                    .filter(User.name==self.name).one()
            except NoResultFound:
                self._user = Profile.default_user(self.name)
        return self._user

    @property
    def stats(self):
        """Return all the player's stats."""
        if not self._stats:
            self._stats = dict([
                    (name, endpoint.get_by_name(self.name))
                    for name, endpoint in player_stats.endpoints.iteritems()
                    ])
        return self._stats
    
    @property
    def profile_stats(self):
        """Return the stats specified in the player's show_stats field and with empty servers removed"""
        stats = filter(lambda (name, stats):
                           len(stats) and (not self.show_stats or name in self.show_stats),
                       self.stats.iteritems())
        if not len(stats): return None
        return dict(stats)

    @property
    def avatar(self):
        return avatar.avatar(self.user.mail)
    
    @staticmethod
    def default_profile(name, user=None):
        """Return a default profile for unregistered users"""
        return Profile(
            name=name,
            show_stats=' '.join(player_stats.endpoints.keys()),
            _user=user,
            default=True
        )
    
    @staticmethod
    def default_user(name):
        """Return a default user"""
        user = User(name=name)
        user.default = True
        return user

setattr(User, 'profile', property(lambda self: self._profile or Profile.default_profile(self.name, user=self)))


class Blueprint(flask.Blueprint, object):
    """Our blueprint that will lazy load it's session when in a flask context"""

    def get_by_name(self, name):
        """Load a player profile for name, or the default profile.
        
        This is shorthand for profile = (user.profile or player_profiles.default_profile())
        
        """
        try:
            return player_profiles.session.query(Profile).filter(Profile.name==name).one()
        except NoResultFound:
            return Profile.default_profile(name)


"""Singleton blueprint object"""
player_profiles = Blueprint('player_profiles', __name__, template_folder='templates')

player_profiles.session = sqlalchemy.orm.sessionmaker(current_app.config['ENGINE'])()
    

# Forms :)

def validate_show_stats(form, field):
    invalid = list()
    parts = re.compile('[,\s]+').split(field.data.lower())
    servers = player_stats.endpoints.keys()
    for server in parts:
        if not server in servers:
            invalid.append(server)
    if len(invalid):
        raise ValidationError('Invalid servers: %s'%', '.join(invalid))

ProfileForm = model_form(
    Profile, player_profiles.session,
    field_args={ 'show_stats': {
            'label': 'Displayed stats',
            'description': "You can remove any or all servers from this list to hide them on your profile.",
            'validators': [ Optional(), validate_show_stats ]
            }
        })


# Blueprint routes

@player_profiles.route('/profile/<name>')
def show_profile(name):
    profile = player_profiles.get_by_name(name)
    if not profile.user.__dict__.get('default') and not profile.user.name == name:
        # Redirect to preferred spelling url
        return redircet(url_for("player_profiles.show-profile", name=profile.user.name))
    if profile.default and not sum(map(lambda (_, stats): len(stats), profile.stats.items())):
        # Error out if the default profile is loaded and there are no stats.
        # This should be the case if the player has never logged onto any of the servers.
        abort(404)
    return render_template('show_profile.html', profile=profile)

@player_profiles.route('/profile', methods=('GET', 'POST'))
@flask_login.login_required
def edit_profile():
    profile = player_profiles.session.query(Profile).filter(Profile.name==flask_login.current_user.name).one()
    form = ProfileForm(request.form, profile)
    if request.method == 'POST' and form.validate():
        form.populate_obj(profile)
        profile.show_stats = ' '.join(re.compile('[,\s]+').split(profile.show_stats.lower()))
        player_profiles.session.add(profile)
        player_profiles.session.commit()
        flash('Profile saved')
        return redirect(url_for('player_profiles.edit_profile'))
    return render_template('edit_profile.html', form=form)

