from flask import Blueprint, render_template, current_app, abort
import sqlalchemy
import sqlalchemy.orm
from sqlalchemy.types import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column
from sqlalchemy.orm.exc import NoResultFound
import flask_login as login


player_profiles = Blueprint('player_profiles', __name__,
                            template_folder='templates',
                            static_folder='static',
                            static_url_path='/player_profiles/static')


# Routes

@player_profiles.route('/profile')
@login.login_required
def edit_profile():
    return render_template('edit_profile.html', profile=get_by_name(login.current_user.get_name()))

@player_profiles.route('/profile/<player>')
def show_profile(player):
    try:
        return render_template('show_profile.html', profile=get_by_name(player))
    except NoResultFound:
        abort(404)


# Blueprint helpers

Base = declarative_base()

class Profile(Base):
    __tablename__ = 'player_profiles'
    name = Column(String(16), primary_key=True)

__engine__ = None
__session__ = None

def get_session():
    global __session__
    if not __session__:
        global __engine__
        if not __engine__:
            __engine__ = current_app.config['ENGINE']
            Base.metadata.bind = __engine__
        __session__ = sqlalchemy.orm.create_session(__engine__)
    return __session__

def get_by_name(name):
    return get_session().query(Profile).filter(Profile.name==name).one()
