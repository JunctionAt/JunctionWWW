"""Miscelaneous static pages"""

from datetime import datetime, timedelta
from threading import Thread, Lock
import requests
import json
from flask import Blueprint, Markup, render_template, url_for, current_app, g, request, redirect, send_file
from sqlalchemy import desc

from blueprints.base import db
#from blueprints.player_groups import player_groups, Group

static_pages = Blueprint('static_pages', __name__,
                         template_folder='templates',
                         static_folder='static',
                         # This should work without having to munge the static path,
                         # but the application's static path takes precedence
                         # if no url_prefix is specified:
                         # https://github.com/mitsuhiko/flask/issues/348
                         static_url_path='/static_pages/static')

client = requests.session()
client.post('https://ssl.reddit.com/api/login',
            data=dict(user="JunctionBot",
                      passwd="^pOd9$qHU&t8J#t8Nd#m",
                      api_type='json'))

posts = type('posts', (object,), dict(data=[], refresh=datetime.utcnow(), fetching=False))
lock = Lock()

class PostFetchThread(Thread):
    def run(self):
        lock.acquire()
        if posts.refresh < datetime.utcnow():
            posts.fetching = True
            posts.data = client.get('http://www.reddit.com/r/junction.json').json['data']['children']
            posts.refresh = datetime.utcnow() + timedelta(0, 10 * 60)
            posts.fetching = False
        lock.release()
                
@static_pages.route('/')
def landing_page():
    #groups = dict(
    #    reduce(
    #        lambda groups, (server, _): groups + [
    #            (server,
    #             db.session.query(Group) \
    #                 .filter(Group.server==server) \
    #                 .order_by(desc(Group.member_count)) \
    #                 .limit(25) \
    #                 .all())],
    #        player_groups.endpoints.iteritems(), []))
    #if not posts.fetching and posts.refresh < datetime.utcnow(): PostFetchThread().start()
    return render_template('index_newer.html')#, posts=map(lambda post: post['data'], posts.data))#, groups=groups)

@static_pages.route('/servers')
def view_servers():
    return render_template('servers.html')