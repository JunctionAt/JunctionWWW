from flask import render_template
from random import shuffle

from .. import blueprint
from models.user_model import User, Role_Group


listings = [
    {"id": "moderator", "name": "Moderators", "description":
        "These players complete modreqs, ban the troublemakers, and set up protections. "
        "Just remember they have a life as well!"},
    {"id": "technical", "name": "Technical Staff", "description":
        "These players are trusted with the keys to the server. "
        "They fixit when something crashes, code our custom plugins, and make sure everything's greased up."},
    {"id": "inactive", "name": "Inactive Staff", "description":
        "These players served as staff on Junction at some point in time. "
        "They haven't been around in a while and therefore have had their powers removed."},
    {"id": "resigned", "name": "Former Staff", "description":
        "These players were former Junction staff members and have left to play as a normal player."},
]


@blueprint.route('/staff/')
def view_staff():
    listings_data = dict()
    for listing in listings:
        data = User.objects(role_groups__in=[Role_Group.objects(name=listing["id"]).first()]).only('name')
        data = list(data)
        shuffle(data)
        listings_data[listing["id"]] = data

    return render_template('staff_view_staff.html', data=listings_data, listings=listings, title="Staff")
