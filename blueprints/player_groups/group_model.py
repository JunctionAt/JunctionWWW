__author__ = 'HansiHE'

from mongoengine import *
from blueprints.auth import user_model
from blueprints.avatar import get_avatar_url

#class Group(Base):
#    """The player group table"""
#
#    __tablename__ = 'player_groups'
#    id = db.Column(db.String(64), primary_key=True)
#    server = db.Column(db.String(16))
#    name = db.Column(db.String(32))
#    display_name = db.Column(db.String(32))
#    created = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
#    mail = db.Column(db.String(60))
#    tagline = db.Column(db.String(256))
#    link = db.Column(db.String(256))
#    info = db.Column(db.Text(1024))
#    public = db.Column(db.Boolean)
#    member_count = db.Column(db.Integer)
#    owners = db.relation(User, secondary=lambda:GroupOwners.__table__, backref="groups_owner")
#    members = db.relation(User, secondary=lambda:GroupMembers.__table__, backref="groups_member")
#    invited_owners = db.relation(User, secondary=lambda:GroupInvitedOwners.__table__, backref="groups_invited_owner")
#    invited_members = db.relation(User, secondary=lambda:GroupInvitedMembers.__table__, backref="groups_invited_member")
#
#    @property
#    def avatar(self):
#        return avatar.avatar(self.mail)
#
#    @staticmethod
#    def confirm(pending):
#        """Returns a copy of pending with a confirmed id"""
#        group = Group(**reduce(
#            lambda kwargs, prop: dict(kwargs.items() + [(prop, getattr(pending, prop))]),
#            [ 'server',
#              'name',
#              'display_name',
#              'mail',
#              'tagline',
#              'link',
#              'info',
#              'public',
#              'member_count',
#              'owners',
#              'members',
#              'invited_owners',
#              'invited_members',
#              ], dict()))
#        group.id = "%s.%s"%(group.server,group.name)
#        return group

class Group(Document):

    gid = StringField()
    server = StringField()
    name = StringField()
    display_name = StringField()
    created = DateTimeField()
    mail = StringField()
    tagline = StringField()
    link = StringField()
    info = StringField()
    public = BooleanField()

    member_count = IntField()

    owners = ListField(ReferenceField(user_model.User, dbref=False, reverse_delete_rule=PULL))
    members = ListField(ReferenceField(user_model.User, dbref=False, reverse_delete_rule=PULL))
    invited_owners = ListField(ReferenceField(user_model.User, dbref=False, reverse_delete_rule=PULL))
    invited_members = ListField(ReferenceField(user_model.User, dbref=False, reverse_delete_rule=PULL))

    #owners = ListField(StringField())
    #members = ListField(StringField())
    #invited_owners = ListField(StringField())
    #invited_members = ListField(StringField())

    meta = {
        'collection': 'player_groups'
    }

    @property
    def avatar(self):
        return "" #TODO: Return a proper URL

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
              'member_count',
              'owners',
              'members',
              'invited_owners',
              'invited_members',
            ], dict()))
        group.id = "%s.%s"%(group.server,group.name)
        return group

#def GroupUserRelation(tablename):
#    """Generate secondary table linking groups to users"""
#
#    return type(tablename, (Base,), dict(
#        __tablename__=tablename,
#        group_id=db.Column(db.String(64), db.ForeignKey(Group.id, ondelete='CASCADE'), primary_key=True),
#        user_name=db.Column(db.String(16), db.ForeignKey(User.name), primary_key=True),))
#
#GroupOwners = GroupUserRelation('player_groups_owners')
#GroupMembers = GroupUserRelation('player_groups_members')
#GroupInvitedOwners = GroupUserRelation('player_groups_invited_owners')
#GroupInvitedMembers = GroupUserRelation('player_groups_invited_members')