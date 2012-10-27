import flask
from flask import Blueprint, abort, request
from flask.ext.principal import Permission, RoleNeed

from blueprints.auth import login_required

from systems import basesystem


bansystems = {"basesystem" : basesystem}

bans = Blueprint('bans', __name__, template_folder="templates")

def getbans(args):
    return str('wat' in args)

def fulllookup(args):
    return str('wat' in args)

methods = {"getbans" : getbans, "fulllookup" : fulllookup}

@bans.route('/bans/<string:method>.json')
#@login_required
def show_logs(method):
    #with Permission(RoleNeed('bans.write')).require(403):
        if method not in methods:
            abort(404)
        return methods[method](request.args)

