import flask
import re
import json
import Queue
from threading import Thread
from flask import Blueprint, abort, request
from flask.ext.principal import Permission, RoleNeed
from blueprints.auth import login_required
from systems import basesystem, testsystem

usernameregex = re.compile('^[a-zA-Z0-9_]+$')
bansystems = {"basesystem" : basesystem, "testsystem" : testsystem}
bans = Blueprint('bans', __name__, template_folder="templates")

def verifyusername(username):
    return len(username)<=16 and usernameregex.match(username)

class ReqThread(Thread):
    def __init__(self, func, queue):
        Thread.__init__(self)
        self.func = func
        self.retqueue = queue

    def run(self):
        self.retqueue.put(self.func())

@bans.route('/bans/getbans.json')
def getbans():
    args = request.args
    if args.has_key('username') and verifyusername(args['username']):
        username = args['username']
    else:
        return json.dumps({'error' : 'The username provided was invalid'})
    response = {'bancount' : 0, 'systems' : {}}
    retqueue = Queue.Queue()
    threads = []
    for key, value in bansystems.items():
        #sysres = value.getbans(username)
        t = ReqThread(lambda: value.getbans(username), retqueue)
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    return json.dumps(retqueue.get())


#methods = {"getbans" : getbans}

#@bans.route('/bans/<string:method>.json')
#@login_required
#def show_logs(method):
#    with Permission(RoleNeed('bans.write')).require(403):
#        if method not in methods:
#            abort(404)
#        return methods[method](request.args)

