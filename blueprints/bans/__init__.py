import flask
import re
import json
import Queue
from threading import Thread
from flask import Blueprint, abort, request
from flask.ext.principal import Permission, RoleNeed
from blueprints.auth import login_required
from systems import minebans, mcbans, mcbouncer

usernameregex = re.compile('^[a-zA-Z0-9_]+$')
bansystems = {"minebans" : minebans, "mcbans" : mcbans, "mcbouncer" : mcbouncer}
bans = Blueprint('bans', __name__, template_folder="templates")

def verifyusername(username):
    return len(username)<=16 and usernameregex.match(username)

def mergedata(retqueue):
    response = {}
    for ret in list(retqueue.queue):
        if ret == None:
            continue
        sysname = ret['_sysname']
        if ret.has_key('bans') and len(ret['bans'])!=0:
            if 'bans' not in response:
                response['bans'] = []
            if 'bancount' not in response:
                response['bancount'] = 0
            for ban in ret['bans']:
                ban['system'] = sysname
                response['bans'].append(ban)
                response['bancount'] += 1
        if ret.has_key('notes') and len(ret['notes'])!=0:
            if 'notes' not in response:
                response['notes'] = []
            if 'notecount' not in response:
                response['notecount'] = 0
            for note in ret['notes']:
                note['system'] = sysname
                response['notes'].append(ban)
                response['notecount'] += 1

    return response

class ReqThread(Thread):
    def __init__(self, func, queue, sysname):
        Thread.__init__(self)
        self.func = func
        self.retqueue = queue
        self.sysname = sysname

    def run(self):
        ret = self.func()
        ret['_sysname'] = self.sysname
        self.retqueue.put(ret)

@bans.route('/bans/getbans.json')
def getbans():
    args = request.args
    if args.has_key('username') and verifyusername(args['username']):
        username = args['username']
    else:
        return json.dumps({'error' : 'The username provided was invalid'})
    retqueue = Queue.Queue()
    threads = []
    for key, value in bansystems.items():
        t = ReqThread(lambda: value.getbans(username), retqueue, key)
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

    return json.dumps(mergedata(retqueue))


#methods = {"getbans" : getbans}

#@bans.route('/bans/<string:method>.json')
#@login_required
#def show_logs(method):
#    with Permission(RoleNeed('bans.write')).require(403):
#        if method not in methods:
#            abort(404)
#        return methods[method](request.args)

