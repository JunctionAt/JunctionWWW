import flask
import re
import json
import Queue
from threading import Thread
from flask import Blueprint, abort, request
from flask.ext.principal import Permission, RoleNeed
from blueprints.auth import login_required
from blueprints.base import db
from systems import minebans, mcbans, mcbouncer
from ban_model import Ban
from blueprints.base import db

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
                response['notes'].append(note)
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
        if ret != None:
            ret['_sysname'] = self.sysname
        self.retqueue.put(ret)

@bans.route('/bans/global/getbans.json')
def getglobalbans():
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

@bans.route('/bans/global/getnotes.json')
def getglobalnotes():
    args = request.args
    if args.has_key('username') and verifyusername(args['username']):
        username = args['username']
    else:
        return json.dumps({'error' : 'The username provided was invalid'})
    retqueue = Queue.Queue()
    threads = []
    for key, value in bansystems.items():
        t = ReqThread(lambda: value.getnotes(username), retqueue, key)
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

    return json.dumps(mergedata(retqueue))

@bans.route('/bans/global/fulllookup.json')
def fullgloballookup():
    args = request.args
    if args.has_key('username') and verifyusername(args['username']):
        username = args['username']
    else:
        return json.dumps({'error' : 'The username provided was invalid'})
    retqueue = Queue.Queue()
    threads = []
    for key, value in bansystems.items():
        t = ReqThread(lambda: value.getnotes(username), retqueue, key)
        t.start()
        threads.append(t)
        t = ReqThread(lambda: value.getbans(username), retqueue, key)
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

    return json.dumps(mergedata(retqueue))

@bans.route('/bans/local/getbans.json')
def getlocalbans():
    args = request.args
    if args.has_key('username') and verifyusername(args['username']):
        username = args['username']
    else:
        return json.dumps({'error' : 'The username provided was invalid'})
    bans = db.session.query(Ban).filter(Ban.banned==args['username'])
    count = bans.count()
    response = {'bancount' : count}
    if count > 0:
        response['bans'] = []
        for ban in bans:
            retban = {}
            retban['uid'] = ban.id
            retban['issuer'] = ban.issuer
            retban['time'] = ban.gettime()
            retban['reason'] = ban.reason
            retban['server'] = ban.server
            response['bans'].append(retban)
    return json.dumps(response)

@bans.route('/bans/local/banuser.json')
def banuser():
    args = request.args
    if args.has_key('banned') and verifyusername(args['banned']):
        banned = args['banned']
    else:
        return json.dumps({'error' : 'The user to ban that was provided is invalid.'})
    if args.has_key('issuer') and (verifyusername(args['issuer']) or (args['issuer'][:1]=='[' and args['issuer'][1:]==']')):
        issuer = args['issuer']
    else:
        return json.dumps({'error' : 'The issuer provided was invalid.'})
    if args.has_key('reason') and args['reason'].__len__()<=500:
        reason = args['reason']
    else:
        return json.dumps({'error' : 'The reason provided was invalid.'})
    if args.has_key('server') and args['server'].__len__()<=100:
        server = args['server']
    else: 
        return json.dumps({'error' : 'The reason provided was invalid.'})
    ban = Ban(issuer, banned, reason, server)
    db.session.add(ban)
    db.session.commit()

#methods = {"getbans" : getbans}

#@bans.route('/bans/<string:method>.json')
#@login_required
#def show_logs(method):
#    with Permission(RoleNeed('bans.write')).require(403):
#        if method not in methods:
#            abort(404)
#        return methods[method](request.args)

