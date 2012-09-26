import flask
import flask_login
from flask import Blueprint, render_template, request, current_app, abort, flash, redirect, url_for
import sqlalchemy
import sqlalchemy.orm
from sqlalchemy.orm import relation
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import *
from sqlalchemy import Column
from sqlalchemy.orm.exc import NoResultFound
from wtalchemy.orm import model_form
import re

from blueprints.base import Base
from blueprints.auth.user_model import User


def player_groups(servers=[]):
    """Create routes for all group endpoints defined in servers
    
    Returns the blueprint for easy setup.
    
    """
    
    for server in servers:
        player_groups.endpoints[server['name']] = Endpoint(**server)

    return player_groups.blueprint


class Group(Base):
    """The player group table"""

    __tablename__ = 'player_groups'
    id = Column(String(49), primary_key=True)
    server = Column(String(16))
    name = Column(String(32))
    display_name = Column(String(32))
    mail = Column(String(256))
    tagline = Column(String(256))
    info = Column(Text(1024))
    link = Column(String(256))
    owners = relation(User, secondary=lambda:GroupOwners.__table__)
    members = relation(User, secondary=lambda:GroupMembers.__table__)
    
class GroupOwners(Base):
    """Secondary table linking groups to users as owners"""

    __tablename__ = 'player_groups_owners'
    group_id = Column(String(49), ForeignKey(Group.id), primary_key=True)
    user_name = Column(String(16), ForeignKey(User.name), primary_key=True)

class GroupMembers(Base):
    """Secondary table linking groups to users as members"""

    __tablename__ = 'player_groups_members'
    group_id = Column(String(49), ForeignKey(Group.id), primary_key=True)
    user_name = Column(String(16), ForeignKey(User.name), primary_key=True)


# Endpoints
player_groups.endpoints = dict()

# Blueprint
player_groups.blueprint = Blueprint('player_groups', __name__, template_folder='templates')

player_groups.session = sqlalchemy.orm.sessionmaker(current_app.config['ENGINE'])()


class Endpoint(object):
    """Wrapper to distinguish server groups"""

    def __init__(self, name,
                 group='group',
                 groups='groups',
                 member='member',
                 members='members',
                 owner='owner',
                 owners='owners'):
        """Create a player_groups endpoint for server name"""

        self.server = name
        self.group = group
        self.groups = groups
        self.member = member
        self.members = members
        self.owner = owner
        self.owners = owners

        def show_group(group):
            """Show group page, endpoint specific """
            try: group = player_groups.session.query(Group).filter(Group.id=="%s.%s"%(self.server,group)).one()
            except NoResultFound: abort(404)
            return render_template('show_group.html', endpoint=self, group=group)
        player_groups.blueprint.add_url_rule('/%s/%s/<group>'%(self.server, self.group), '%s_show_group'%self.server, show_group)
        
        @flask_login.login_required
        def edit_group(group):
            """Edit group page, endpoint specific"""
            try: group = player_groups.session.query(Group).filter(Group.id=="%s.%s"%(self.server,group)).one()
            except NoResultFound: abort(404)
            user = player_groups.session.query(User).filter(User.name==flask_login.current_user.name).one()
            if not user in group.owners: abort(403)
            form = GroupForm(request.form, group)
            if request.method == 'POST' and form.validate():
                form.populate_obj(group)
                player_groups.session.add(group)
                player_groups.session.commit()
                flash('%s saved'%self.group.capitalize())
                return redirect(url_for('player_groups.edit_group', group=group))
            return render_template('edit_group.html', endpoint=self, form=form)
        player_groups.blueprint.add_url_rule('/%s/%s/<group>/edit'%(self.server, self.group), '%s_edit_group'%self.server, edit_group)

        @flask_login.login_required
        def register_group():
            """Register group page, endpoint specific"""
            group = Group()
            form = GroupForm(request.form, group)
            user = player_groups.session.query(User).filter(User.name==flask_login.current_user.name).one()
            if request.method == 'POST' and form.validate():
                form.populate_obj(group)
                player_groups.session.add(group)
                player_groups.session.commit()
                flash('%s registerd'%self.group.capitalize())
                return redirect(url_for('player_groups.show_group', group=group))
            return render_template('register_group.html', endpoint=self, form=form)
        player_groups.blueprint.add_url_rule('/%s/%s/register'%(self.server, self.groups), '%s_register_group'%self.server, register_group)


@player_groups.blueprint.route('/groups/<server>/show/<group>', methods=('GET', 'POST'))
def show_group(server, group):
    """Redirects to preferred url of server"""
    endpoint = player_groups.endpoints.get(server)
    if endpoint:
        return redirect(url_for('player_groups.%s_show_group'%endpoint.server, group=group))
    abort(404)

@player_groups.blueprint.route('/groups/<server>/edit/<group>', methods=('GET', 'POST'))
def edit_group(server, group):
    """Redirects to preferred url of server"""
    endpoint = player_groups.endpoints.get(server)
    if endpoint:
        return redirect(url_for('player_groups.%s_edit_group'%endpoint.server, group=group))
    abort(404)

@player_groups.blueprint.route('/groups/<server>/register', methods=('GET', 'POST'))
@flask_login.login_required
def register_group(server):
    """Redirects to preferred url of server"""
    endpoint = player_groups.endpoints.get(server)
    if endpoint:
        return redirect(url_for('player_groups.%s_register_group'%endpoint.server))
    abort(404)

# This is next
GroupForm = model_form(Group, player_groups.session)
