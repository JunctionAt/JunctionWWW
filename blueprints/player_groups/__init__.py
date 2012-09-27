import flask
import flask_login
from flask import Blueprint, render_template, request, current_app, abort, flash, redirect, url_for
import sqlalchemy
import sqlalchemy.orm
from sqlalchemy.orm import relation
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import *
from sqlalchemy.sql.expression import and_
from sqlalchemy import Column
from sqlalchemy.orm.exc import NoResultFound
from wtforms.validators import Optional, Email, ValidationError
from wtalchemy.orm import model_form
import re

from blueprints.base import Base
from blueprints.auth.user_model import User
from blueprints.avatar import avatar


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
    id = Column(String(64), primary_key=True)
    server = Column(String(16))
    name = Column(String(32))
    display_name = Column(String(32))
    mail = Column(String(256))
    tagline = Column(String(256))
    link = Column(String(256))
    info = Column(Text(1024))
    public = Column(Boolean)
    owners = relation(User, secondary=lambda:GroupOwners.__table__)
    members = relation(User, secondary=lambda:GroupMembers.__table__)
    invited_owners = relation(User, secondary=lambda:GroupInvitedOwners.__table__)
    invited_members = relation(User, secondary=lambda:GroupInvitedMembers.__table__)
    
    @property
    def avatar(self):
        return avatar(self.mail)


def GroupUserRelation(tablename):
    """Generate secondary table linking groups to users"""
    
    return type(tablename, (Base,), {
            '__tablename__': tablename,
            'group_id': Column(String(64), ForeignKey(Group.id), primary_key=True),
            'user_name': Column(String(16), ForeignKey(User.name), primary_key=True)
            })

GroupOwners = GroupUserRelation('player_groups_owners')
GroupMembers = GroupUserRelation('player_groups_members')
GroupInvitedOwners = GroupUserRelation('player_groups_invited_owners')
GroupInvitedMembers = GroupUserRelation('player_groups_invited_members')


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
            try: group = player_groups.session.query(Group).filter(Group.id.in_([
                        "%s.%s"%(self.server,group),
                        "%s.pending.%s"%(self.server,group)
                        ])).first()
            except NoResultFound: abort(404)
            if not group.name == group:
                # Redirect to preferred spelling
                return redirect(url_for('player_groups.%s_show_group'%self.server, group=group.name))
            return render_template('show_group.html', endpoint=self, group=group)
        player_groups.blueprint.add_url_rule('/%s/%s/<group>'%(self.server, self.group), '%s_show_group'%self.server, show_group)

        
        GroupForm = model_form(
            Group, player_groups.session, exclude=[ 'server', 'name', 'owners', 'members' ],
            field_args={
                'mail': {
                    'description': 'Optional contact email for your %s. Will allow you a custom avatar.'%self.group,
                    'validators': [Optional(), Email()]
                    },
                })
        
        @flask_login.login_required
        def edit_group(group):
            """Edit group page, endpoint specific"""
            try: group = player_groups.session.query(Group).filter(Group.id.in_([
                        "%s.%s"%(self.server,group),
                        "%s.pending.%s"%(self.server,self.group)
                        ])).first()
            except NoResultFound: abort(404)
            if not group.name == group:
                # Redirect to preferred spelling
                return redirect(url_for('player_groups.%s_edit_group'%self.server, group=group.name))
            user = player_groups.session.query(User).filter(User.name==flask_login.current_user.name).one()
            if not user in group.owners: abort(403)
            form = GroupForm(request.form, group)
            if request.method == 'POST' and form.validate():
                form.populate_obj(group)
                # Make ownership and membership mutually exclusive
                group.invited_owners = list(set(group.invited_owners + [user]))
                group.invited_members = list(set(group.invited_members) - set(group.invited_owners))
                # Remove uninvited players, promote & demote
                _owners = set(group.owners)
                _members = set(group.members)
                group.owners = list((_owners & set(group.invited_owners)) |
                                    (set(group.invited_owners) & _members))
                group.members = list((_members & set(group.invited_members)) |
                                      (set(group.invited_members) & _owners))
                # Commit
                player_groups.session.add(group)
                player_groups.session.commit()
                # Done
                flash('%s saved'%self.group.capitalize())
                return redirect(url_for('player_groups.%s_edit_group'%self.server, group=group))
            return render_template('edit_group.html', endpoint=self, form=form)
        player_groups.blueprint.add_url_rule('/%s/%s/<group>/edit'%(self.server, self.group),
                                             '%s_edit_group'%self.server, edit_group, methods=('GET', 'POST'))
        
        @flask_login.login_required
        def register_group():
            """Register group page, endpoint specific"""
            group = Group()
            form = GroupForm(request.form, group)
            user = player_groups.session.query(User).filter(User.name==flask_login.current_user.name).one()
            if request.method == 'POST' and form.validate():
                form.populate_obj(group)
                group.display_name = re.sub(r'\s+', ' ', name.strip())
                group.name = re.sub(r'\s+', '_', re.sub(r'[^a-zA-Z0-9]+', '', group.display_name))
                group.id = "%s.pending.%s"%(self.server, group.name)
                # Make ownership and membership mutually exclusive
                group.invited_owners = list(set(group.invited_owners + [user]))
                group.invited_members = list(set(group.invited_members) - set(group.invited_owners))
                # Registree is a confirmed owner
                group.owners = [ user ]
                # commit
                player_groups.session.add(group)
                player_groups.session.commit()
                # Done
                flash('%s registerd'%self.group.capitalize())
                return redirect(url_for('player_groups.%s_show_group'%self.server, group=group))
            return render_template('edit_group.html', endpoint=self, form=form, register=True)
        player_groups.blueprint.add_url_rule('/%s/%s/register'%(self.server, self.groups),
                                             '%s_register_group'%self.server, register_group, methods=('GET', 'POST'))
        
        @flask_login.login_required
        def join_group(group):
            """Join group page, endpoint specific"""
            try: group = player_groups.session.query(Group).filter(Group.id.in_([
                        "%s.%s"%(self.server,group),
                        "%s.pending.%s"%(self.server,self.group)
                        ])).first()
            except NoResultFound: abort(404)
            if not group.name == group:
                # Redirect to preferred spelling
                return redirect(url_for('player_groups.%s_join_group'%self.server, group=group.name))
            user = player_groups.session.query(User).filter(User.name==flask_login.current_user.name).one()
            if not user in group.members and not user in group.owners:
                if request.method == 'POST':
                    if not group.public and user in group.invited_owners:
                        group.owners.append(user)
                    elif group.public or user in group.invited_members:
                        group.members.append(user)
                        # Maintain invited status for members of public groups
                        group.invited_members = list(set(group.invited_members + [ user ]))
                    else:
                        abort(403)
                    # Check for confirmation of group registration
                    if group.id == "%s.pending.%s"%(self.server,self.group):
                        group.id = "%s.%s"%(self.server,self.group)
                    player_groups.session.add(group)
                    player_groups.session.commit()
                    flash("You have joined %s"%group.display_name)
                    return redirect(url_for('player_groups.%s_show_group'%self.server, group=group))
                return render_template('join_group.html', endpoint=self, group=group)
            abort(403)
        player_groups.blueprint.add_url_rule('/%s/%s/<group>/join'%(self.server, self.group),
                                             '%s_join_group'%self.server, join_group, methods=('GET', 'POST'))
            


@player_groups.blueprint.route('/groups/<server>/show/<group>')
def show_group(server, group):
    """Redirects to preferred url of server"""
    endpoint = player_groups.endpoints.get(server)
    if endpoint:
        return redirect(url_for('player_groups.%s_show_group'%endpoint.server, group=group))
    abort(404)

@player_groups.blueprint.route('/groups/<server>/edit/<group>')
def edit_group(server, group):
    """Redirects to preferred url of server"""
    endpoint = player_groups.endpoints.get(server)
    if endpoint:
        return redirect(url_for('player_groups.%s_edit_group'%endpoint.server, group=group))
    abort(404)

@player_groups.blueprint.route('/groups/<server>/register')
def register_group(server):
    """Redirects to preferred url of server"""
    endpoint = player_groups.endpoints.get(server)
    if endpoint:
        return redirect(url_for('player_groups.%s_register_group'%endpoint.server))
    abort(404)
