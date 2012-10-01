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

from blueprints.base import Base, session
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
    hide_group_invitations = Column(Boolean)
    default = False
    
    _user = relation(User, backref=backref('_profile', uselist=False), lazy=False)
    _stats = None
    
    @property
    def display_link(self):
        if not self.link: return None
        if re.match('^https?://', self.link):
            return (self.link, re.sub('^https?://', ''))
        return ("http://%s"%self.link, self.link)

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
                self._user = session.query(User) \
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
        profile = Profile(
            name=name,
            show_stats=' '.join(player_stats.endpoints.keys()),
            _user=user
        )
        profile.default = True
        return profile
    
    @staticmethod
    def default_user(name):
        """Return a default user"""
        user = User(name=name)
        user.is_anonymous = lambda: True # I know, it's not really anonymous if it has a name
        
        return user


setattr(User, 'profile', property(lambda self: self._profile or Profile.default_profile(self.name, user=self)))


class Blueprint(flask.Blueprint, object):

    def register(self, *args, **kwargs):

        @self.route('/profile/<name>')
        def show_profile(name):
            try:
                profile = session.query(User).filter(User.name==name).one().profile
            except NoResultFound:
                # Look for stats
                stat = reduce(lambda stat, (server, endpoint):
                                  stat or session.query(endpoint.model).filter(endpoint.model.player==name).first(),
                              player_stats.endpoints.iteritems(), None)
                if not stat: abort(404)
                profile = Profile.default_profile(stat.player)
            if not profile.user.name == name:
                # Redirect to preferred caps
                return redirect(url_for("player_profiles.show_profile", name=profile.user.name))
            return render_template('show_profile.html', profile=profile)

        @self.route('/profile', methods=('GET', 'POST'))
        @flask_login.login_required
        def edit_profile():
            profile = flask_login.current_user.profile
            profile.show_stats = ' '.join(filter(lambda stats: stats in player_stats.endpoints.keys(), profile.show_stats.split(' ')))
            form = ProfileForm(request.form, profile)
            if request.method == 'POST' and form.validate():
                form.populate_obj(profile)
                profile.show_stats = ' '.join(re.compile('[,\s]+').split(profile.show_stats.lower()))
                session.add(profile)
                session.commit()
                flash('Profile saved')
                return redirect(url_for('player_profiles.edit_profile'))
            return render_template('edit_profile.html', form=form)

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
            Profile, session,
            field_args=dict(show_stats=dict(
                    label='Displayed stats',
                    description="You can remove any or all servers from this list to hide them on your profile.",
                    validators=[ Optional(), validate_show_stats ])))

        return super(Blueprint, self).register(*args, **kwargs)


"""Singleton blueprint object"""
player_profiles = Blueprint('player_profiles', __name__, template_folder='templates')

