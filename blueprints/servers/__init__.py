__author__ = 'williammck'

from flask import Blueprint, current_app

from models.servers_model import Server

blueprint = Blueprint('servers', __name__, template_folder='templates')

@current_app.context_processor
def inject_servers():
    return dict(servers=Server.objects())

from views import view_servers
