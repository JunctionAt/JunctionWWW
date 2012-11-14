"""
Profiles
--------

Endpoints for getting and editing player profile data.
"""

import flask
import flask_login
from flask import Blueprint, jsonify, render_template, request, current_app, abort, flash, redirect, url_for
from werkzeug.datastructures import MultiDict
from sqlalchemy.orm.exc import *
from wtalchemy.orm import model_form
from wtforms.validators import Optional, Length, ValidationError
import re

from blueprints.base import Base, session, db
from blueprints.auth import login_required
from blueprints.auth.user_model import User
from blueprints.player_stats import player_stats
from blueprints.avatar import avatar
from blueprints.api import apidoc

class Profile(Base, object):
    """The player profile table"""

    __tablename__ = 'player_profiles'
    name = db.Column(db.String(16), db.ForeignKey(User.name), primary_key=True)
    realname = db.Column(db.String(64))
    location = db.Column(db.String(64))
    tagline = db.Column(db.String(256))
    link = db.Column(db.String(256))
    reddit_name = db.Column(db.String(20))
    show_stats = db.Column(db.String(64))
    hide_group_invitations = db.Column(db.Boolean)
    default = False
    
    _user = db.relation(User, backref=db.backref('_profile', uselist=False), lazy=False)
    _stats = None
    
    @property
    def display_link(self):
        if not self.link: return None
        if self.link.beginswith('http://'):
            return self.link[7:]
        elif self.link.beginswith('https://'):
            return self.link[8:]
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
        stats = self.stats
        if not self.user.is_anonymous():
            stats = filter(lambda (name, stats): name in self.show_stats, stats.iteritems())
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
        return user


setattr(User, 'profile', property(lambda self: self._profile or Profile.default_profile(self.name, user=self)))

player_profiles = Blueprint('player_profiles', __name__, template_folder='templates')

@apidoc(__name__, player_profiles, '/profile/<player>.json', endpoint='show_profile', defaults=dict(ext='json'))
def show_profile_api(player, ext):
    """Returns an object with a primary key being the preferred display name of ``player`` containing the profile's public fields. Eg.:

    .. code-block::

       {
           "wiggitywhack": {
               "tagline": "indietechnohippie",
               "realname": "John Driscoll",
               "link": "twitter.com/johndriskull",
               "location": "California"
           }
       }
    """

@player_profiles.route('/profile/<player>', defaults=dict(ext='html'))
def show_profile(player, ext):
    try:
        profile = session.query(User).filter(User.name==player).one().profile
    except NoResultFound:
        if ext == "json": abort(404)
        # Look for stats
        stat = reduce(lambda stat, (server, endpoint):
                          stat or session.query(endpoint.model).filter(endpoint.model.player==player).first(),
                      player_stats.endpoints.iteritems(), None)
        if not stat: abort(404)
        profile = Profile.default_profile(stat.player)
    if not profile.user.name == player:
        # Redirect to preferred caps
        return redirect(url_for("player_profiles.show_profile", player=profile.user.name, ext=ext)), 301
    if ext == 'html':
        return render_template('show_profile.html', profile=profile)
    elif ext == 'json':
        # compile a dictionary to serve
        p = dict()
        if profile.realname: p['realname']=profile.realname
        if profile.location: p['location']=profile.location
        if profile.tagline: p['tagline']=profile.tagline
        if profile.reddit_name: p['reddit_name']=profile.reddit_name
        if profile.link: p['link']=profile.link
        return jsonify({profile.name:p})
    abort(404)
    
@apidoc(__name__, player_profiles, '/profile.json', endpoint='edit_profile', defaults=dict(ext='json'))
@login_required
def edit_profile_get_api(ext):
    """Used by the current player to get all editable fields in their profile."""

@apidoc(__name__, player_profiles, '/profile.json', endpoint='edit_profile', methods=('POST',), defaults=dict(ext='json'))
def edit_profile_post_api(ext):
    """Used by the current player to set profile fields from the request body."""

@player_profiles.route('/profile', defaults=dict(ext='html'), methods=('GET', 'POST'))
@login_required
def edit_profile(ext):
    profile = flask_login.current_user.profile
    profile.show_stats = ' '.join(filter(lambda stats: stats in player_stats.endpoints.keys(), profile.show_stats.split(' ')))
    form = ProfileForm(MultiDict(request.json) or request.form, profile, csrf_enabled=False)
    if request.method == 'POST' and form.validate():
        profile.tagline = form._fields['tagline'].data or profile.tagline
        profile.location = form._fields['location'].data or profile.location
        profile.link = form._fields['link'].data or profile.link
        profile.reddit_name = form._fields['reddit_name'].data or profile.reddit_name
        profile.hide_group_invitations = form._fields['hide_group_invitations'].data or profile.hide_group_invitations
        if form._fields['show_stats']:
            profile.show_stats = ' '.join(re.split(r'[,\s]+', form._fields['show_stats'].data.lower()))
        session.add(profile)
        try:
            session.commit()
        except:
            session.rollback()
            abort(500)
        if ext == 'html': flash('Profile saved')
        return redirect(url_for('player_profiles.edit_profile', ext=ext)), 303
    if ext == 'json':
        if request.method == 'POST':
            return jsonify(
                fields=reduce(lambda errors, (name, field):
                                  errors if not len(field.errors) else errors + [dict(name=name, errors=field.errors)],
                              form._fields.iteritems(),
                              list())), 400
        return jsonify(profile=dict(
                    realname=profile.realname,
                    location=profile.location,
                    tagline=profile.tagline,
                    link=profile.link,
                    show_stats=profile.show_stats,
                    reddit_name=profile.reddit_name,
                    hide_group_invitations=profile.hide_group_invitations))
    return render_template('edit_profile.html', form=form)

def validate_show_stats(form, field):
    invalid = list()
    parts = re.split('[,\s]+', field.data.lower())
    servers = player_stats.endpoints.keys()
    for server in parts:
        if not server in servers:
            invalid.append(server)
    if len(invalid):
        raise ValidationError('Invalid servers: %s'%', '.join(invalid))

ProfileForm = model_form(
    Profile, session,
    field_args=dict(
        show_stats=dict(
            label='Displayed stats',
            description="You can remove any or all servers from this list to hide them on your profile.",
            validators=[ Optional(), validate_show_stats ]),
        reddit_name=dict(
            validators=[ Optional(), Length(min=3, max=20) ])))
