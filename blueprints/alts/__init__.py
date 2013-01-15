__author__ = 'HansiHE'

from flask import Blueprint, request, render_template, abort, send_file, flash, redirect, url_for
from blueprints.auth import login_required
import json
from alts_model import PlayerAlt

alts = admin = Blueprint('admin', __name__, template_folder='templates')

def verify_arg(list, arg):
    pass

def construct_error(error):
    return json.dumps({
        'success': False,
        'error': error
    })

def construct_success():
    return json.dumps({
        'success': True
    })

#
@alts.route('/alts/link_user_ip.json')
def link_user_ip():
    args = request.args

    try:
        username = args['username']
    except IndexError:
        return construct_error("No field 'username' provided.")
    try:
        ip = args['ip']
    except IndexError:
        return construct_error("No field 'ip' provided.")

    user = PlayerAlt.objects(username=username).first()

    if user is None:
        user = PlayerAlt(username=username)
    elif ip in user.ips:
        return construct_success()

    user.ips.append(ip)
    user.save


def get_alts_user():
    args = request.args

    try:
        username = args['username']
    except IndexError:
        return construct_error("No field 'username' provided.")

    user = PlayerAlt.objects(username=username).first()

    if user is None:
        return json.dumps({
            'success': True,
            'ips': []
        })

    return json.dumps({
        'success': True,
        'ips': user.ips
    })

def get_alts_ip():
    args = request.args

    try:
        ip = args['ip']
    except IndexError:
        return construct_error("No field 'ip' provided.")

    users = PlayerAlt.objects(ips__in=ip)

    if len(users) == 0:
        return json.dumps({
            'success': True,
            'usernames': []
        })

    usernames = []
    for user in users:
        usernames.append(user.username)

    return json.dumps({
        'success': True,
        'usernames': usernames
    })