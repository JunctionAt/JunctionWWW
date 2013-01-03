from mongoengine import *

class User(Document):
    email = StringField(required=True)
    username = StringField()
    active = BooleanField()
    api_public_key = StringField()
    api_private_key = StringField()
    permissions = ListField(StringField())

class Avatar(object):
    """
    The flask.app representation of a user in the authentication realm.
    Im trying to keep flask logic separate from database logic so that the database layer can be
    easily swapped out if someone so wished.
    """
    def __init__(self, email, username, active, permissions, db_reference):
        self.username = username
        self.active = active
        self.email = email
        self.authd = True
        self.permissions = permissions
        self.user_in_db = db_reference

    def is_authenticated(self):
        """Has completed the login phase, the user is officially auth'd"""
        return self.authd

    def is_active(self):
        """Indicate if the user is active and allowed to login, if not true login fails."""
        return self.active

    def is_anonymous(self):
        """I am not a number I am a man!"""
        return False

    def get_id(self):
        """Get the unique id for a user, in this case the email."""
        return self.email

def get_user_by_id(user_id):
    """
    Return an Avatar for the given userid, this should not fail as it is called *after* get_user
    and get_user will always return an Avatar.
    """
    user = User.objects(email=user_id).first()
    return Avatar(user.email, user.username, user.active, user.permissions, user)

def get_user(data):
    """Return or create a user from data handed to us by Mozilla's Persona"""
    if data['status'] == "okay":
        # get user or create
        email = data['email']
        current_user = User.objects(email=email).first()
        print current_user
        if current_user is None:
            # User doesn't exist. Create user now
            current_user = User(email=email, username=email.split("@")[0], active=True)
            current_user.save()
        return Avatar(current_user.email, current_user.username, current_user.active, current_user.permissions, current_user)
    else:
        return None # Failed to auth with persona
