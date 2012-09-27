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
from wtforms.validators import Required, Optional, Email, ValidationError
from wtalchemy.orm import model_form
from flaskext.markdown import Markdown
import re

from blueprints.base import Base
from blueprints.auth.user_model import User
from blueprints.avatar import avatar

Markdown(current_app)

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

    @staticmethod
    def confirm(pending):
        """Returns a copy of pending with a confirmed id"""
        group = Group(**reduce(
                lambda kwargs, prop: dict(kwargs.items() + [(prop, getattr(pending, prop))]),
                [ 'server',
                  'name',
                  'display_name',
                  'mail',
                  'tagline',
                  'link',
                  'info',
                  'public',
                  'owners',
                  'members',
                  'invited_owners',
                  'invited_members',
                  ], {}))
        group.id = "%s.%s"%(group.server,group.name)
        return group


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

        @player_groups.blueprint.route('/%s/%s/<name>'%(self.server, self.group),
                                       endpoint='%s_show_group'%self.server)
        def show_group(name):
            """Show group page, endpoint specific """
            try: group = player_groups.session.query(Group).filter(Group.id.in_([
                        "%s.%s"%(self.server,name),
                        "%s.pending.%s"%(self.server,name)
                        ])).first()
            except NoResultFound: abort(404)
            if not group.name == name:
                # Redirect to preferred caps
                return redirect(url_for('player_groups.%s_show_group'%self.server, name=group.name))
            return render_template('show_group.html', endpoint=self, group=group)

        def validate_display_name(form, field):
            display_name = re.sub(r'\s+', ' ', field.data.display_name.strip())
            name = re.sub(r'\s+', '_', re.sub(r'[^a-zA-Z0-9]+', '', display_name))
            id = "%s.%s"%(self.server, name)
            if player_groups.session.query(Group).filter(Group.id==id).count() > 0:
                raise ValidationError("%s name not available."%self.group.capitalize())
            
        self.validate_display_name = validate_display_name
        
        def group_form(register=False):
            exclude = [ 'server', 'name', 'owners', 'members' ]
            if not register: exclude.append('display_name')
            return model_form(
                Group, player_groups.session, exclude=exclude,
                field_args={
                    'display_name': {
                        'label': '%s name'%self.group,
                        'validators': [ Required(), self.validate_display_name ]
                        },
                    'public': {
                        'label': 'Open registration',
                        'description': 'Check this to allow anyone to join your %s without prior invitation.'%self.group
                        },
                    'mail': {
                        'description': 'Optional contact email for your %s. Will allow you a custom avatar.'%self.group,
                        'validators': [Optional(), Email()]
                        },
                    'invited_owners': {
                        'label': self.owners.capitalize()
                        },
                    'invited_members': {
                        'label': self.members.capitalize()
                        },
                    })

        GroupEditForm = group_form()
        GroupRegisterForm = group_form(register=True)
        
        @player_groups.blueprint.route('/%s/%s/<name>/edit'%(self.server, self.group),
                                       endpoint='%s_edit_group'%self.server,
                                       methods=('GET', 'POST'))
        @flask_login.login_required
        def edit_group(name):
            """Edit group page, endpoint specific"""
            try: group = player_groups.session.query(Group).filter(Group.id.in_([
                        "%s.%s"%(self.server,name),
                        "%s.pending.%s"%(self.server,name)
                        ])).first()
            except NoResultFound: abort(404)
            user = player_groups.session.query(User).filter(User.name==flask_login.current_user.name).one()
            if not user in group.owners: abort(403)
            form = GroupEditForm(request.form, group)
            if request.method == 'POST' and form.validate():
                form.populate_obj(group)
                # Make ownership and membership mutually exclusive
                group.invited_owners = list(set(group.invited_owners + [user]))
                group.invited_members = list(set(group.invited_members) - set(group.invited_owners))
                # Remove uninvited players, promote & demote
                promotions = set(group.invited_owners) & set(group.members)
                demotions = set(group.invited_members) & set(group.owners)
                group.owners = list(promotions | (set(group.owners) & set(group.invited_owners)))
                group.members = list(demotions | (set(group.members) & set(group.invited_members)))
                # Commit
                player_groups.session.add(group)
                player_groups.session.commit()
                # Done
                flash('%s saved'%self.group.capitalize())
                return redirect(url_for('player_groups.%s_edit_group'%self.server, name=group.name))
            if not group.name == name:
                # Redirect to preferred caps
                return redirect(url_for('player_groups.%s_edit_group'%self.server, name=group.name))
            return render_template('edit_group.html', endpoint=self, form=form, group=group)
        
        @player_groups.blueprint.route('/%s/%s/register'%(self.server, self.groups),
                                       endpoint='%s_register_group'%self.server,
                                       methods=('GET', 'POST'))
        @flask_login.login_required
        def register_group():
            """Register group page, endpoint specific"""
            group = Group()
            form = GroupRegisterForm(request.form, group, register=True)
            user = player_groups.session.query(User).filter(User.name==flask_login.current_user.name).one()
            if request.method == 'POST' and form.validate():
                form.populate_obj(group)
                group.display_name = re.sub(r'\s+', ' ', group.display_name.strip())
                group.server = self.server
                group.name = re.sub(r'\s+', '_', re.sub(r'[^a-zA-Z0-9]+', '', group.display_name))
                group.id = "%s.pending.%s"%(self.server, group.name)
                # Make ownership and membership mutually exclusive
                group.invited_owners = list(set(group.invited_owners + [user]))
                group.invited_members = list(set(group.invited_members) - set(group.invited_owners))
                # Registree is a confirmed owner
                group.owners = [ user ]
                # Delete any pending group registrations of the same id
                player_groups.session.query(Group).filter(Group.id==id).delete()
                # Commit
                player_groups.session.add(group)
                player_groups.session.commit()
                # Done
                flash('%s registration complete pending confirmation by other %s.'%(self.group.capitalize(), self.members))
                return redirect(url_for('player_groups.%s_show_group'%self.server, name=group.name))
            return render_template('edit_group.html', endpoint=self, form=form, register=True)
        
        @player_groups.blueprint.route('/%s/%s/<name>/join'%(self.server, self.group),
                                       endpoint='%s_join_group'%self.server,
                                       methods=('GET', 'POST'))
        @flask_login.login_required
        def join_group(name):
            """Join group page, endpoint specific"""
            try: group = player_groups.session.query(Group).filter(Group.id.in_([
                        "%s.%s"%(self.server,name),
                        "%s.pending.%s"%(self.server,name)
                        ])).first()
            except NoResultFound: abort(404)
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
                    if group.id == "%s.pending.%s"%(self.server,group.name):
                        player_groups.session.delete(group)
                        group = Group.confirm(group)
                    player_groups.session.add(group)
                    player_groups.session.commit()
                    flash("You have joined %s"%group.display_name)
                    return redirect(url_for('player_groups.%s_show_group'%self.server, name=group.name))
                if not group.name == name:
                    # Redirect to preferred caps
                    return redirect(url_for('player_groups.%s_join_group'%self.server, name=group.name))
                return render_template('join_group.html', endpoint=self, group=group)
            abort(403)
            

@player_groups.blueprint.route('/groups/<server>/show/<name>')
def show_group(server, name):
    """Redirects to preferred url of server"""
    endpoint = player_groups.endpoints.get(server)
    if endpoint:
        return redirect(url_for('player_groups.%s_show_group'%endpoint.server, name=name))
    abort(404)

@player_groups.blueprint.route('/groups/<server>/edit/<name>')
def edit_group(server, name):
    """Redirects to preferred url of server"""
    endpoint = player_groups.endpoints.get(server)
    if endpoint:
        return redirect(url_for('player_groups.%s_edit_group'%endpoint.server, name=name))
    abort(404)

@player_groups.blueprint.route('/groups/<server>/register')
def register_group(server):
    """Redirects to preferred url of server"""
    endpoint = player_groups.endpoints.get(server)
    if endpoint:
        return redirect(url_for('player_groups.%s_register_group'%endpoint.server))
    abort(404)
