"""Miscelaneous static pages"""

from datetime import datetime, timedelta
from threading import Thread, Lock
import requests
import json
from flask import Blueprint, Markup, render_template, url_for, current_app, g, request, redirect, send_file
#from sqlalchemy import desc

#from blueprints.player_groups import player_groups, Group

static_pages = Blueprint('static_pages', __name__, template_folder='templates')

#client = requests.session()
#client.post('https://ssl.reddit.com/api/login',
#            data=dict(user="JunctionBot",
#                      passwd="^pOd9$qHU&t8J#t8Nd#m",
#                      api_type='json'))

#posts = type('posts', (object,), dict(data=[], refresh=datetime.utcnow(), fetching=False))
#lock = Lock()

#class PostFetchThread(Thread):
#    def run(self):
#        lock.acquire()
#        if posts.refresh < datetime.utcnow():
#            posts.fetching = True
#            posts.data = client.get('http://www.reddit.com/r/junction.json').json['data']['children']
#            posts.refresh = datetime.utcnow() + timedelta(0, 10 * 60)
#            posts.fetching = False
#        lock.release()

@current_app.errorhandler(404)
def error_404(e):
      return render_template('404.html'), 404

@current_app.errorhandler(403)
def error_403(e):
      return render_template('403.html'), 403

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
    return render_template('index_new.html', title="Home")#, posts=map(lambda post: post['data'], posts.data))#, groups=groups)

@static_pages.route('/servers/')
def view_servers():
    return render_template('servers.html', title="Servers")

@static_pages.route('/favicon.ico')
def favicon():
    return send_file('static/favicon.ico')
