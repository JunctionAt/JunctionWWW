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
from ban_model import Ban, Note
from blueprints.base import db

###################################################################################################
################################# Todo: Add authentication! #######################################
###################################################################################################

usernameregex = re.compile('^[a-zA-Z0-9_]+$')
bansystems = {"minebans" : minebans, "mcbans" : mcbans, "mcbouncer" : mcbouncer}
bans = Blueprint('bans', __name__, template_folder="templates")

#db.create_all()

def verifyusername(username):
    return len(username)<=16 and usernameregex.match(username)

def mergedata(dlist):
    response = {}
    for ret in dlist:
        if ret == None:
            continue
        sysname = ''
        if '_sysname' in ret:
            sysname = ret['_sysname']
        if 'bans' in ret and len(ret['bans'])!=0:
            if 'bans' not in response:
                response['bans'] = []
            if 'bancount' not in response:
                response['bancount'] = 0
            for ban in ret['bans']:
                if sysname is not None:
                    ban['system'] = sysname
                response['bans'].append(ban)
                response['bancount'] += 1
        if 'notes' in ret and len(ret['notes'])!=0:
            if 'notes' not in response:
                response['notes'] = []
            if 'notecount' not in response:
                response['notecount'] = 0
            for note in ret['notes']:
                if sysname is not None:
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

#GLOBAL

#@bans.route('/bans/global/getbans.json')
def getglobalbans(request):
    args = request.args
    if args.has_key('username') and verifyusername(args['username']):
        username = args['username']
    else:
        return json.dumps({'success' : False, 'error' : 'The username provided was invalid'})
    retqueue = Queue.Queue()
    threads = []
    for key, value in bansystems.items():
        t = ReqThread(lambda: value.getbans(username), retqueue, key)
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

    return mergedata(list(retqueue.queue))

#@bans.route('/bans/global/getnotes.json')
def getglobalnotes(request):
    args = request.args
    if args.has_key('username') and verifyusername(args['username']):
        username = args['username']
    else:
        return json.dumps({'success' : False, 'error' : 'The username provided was invalid'})
    retqueue = Queue.Queue()
    threads = []
    for key, value in bansystems.items():
        t = ReqThread(lambda: value.getnotes(username), retqueue, key)
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

    return mergedata(list(retqueue.queue))

#@bans.route('/bans/global/fulllookup.json')
def fullgloballookup(request):
    args = request.args
    if args.has_key('username') and verifyusername(args['username']):
        username = args['username']
    else:
        return json.dumps({'success' : False, 'error' : 'The username provided was invalid'})
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

    return mergedata(list(retqueue.queue))

#LOCAL

#@bans.route('/bans/local/getbans.json')
def getlocalbans(request):
    args = request.args
    if args.has_key('username') and verifyusername(args['username']):
        username = args['username']
    else:
        return json.dumps({'success' : False, 'error' : 'The username provided was invalid'})
    bans = db.session.query(Ban).filter(Ban.username==args['username'])
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
    return response

#@bans.route('/bans/local/banuser.json')
def addban(request):
    args = request.args
    if args.has_key('username') and verifyusername(args['username']):
        username = args['username']
    else:
        return json.dumps({'success' : False, 'error' : 'The username provided was invalid.'})
    if args.has_key('issuer') and (verifyusername(args['issuer']) or (args['issuer'][:1]=='[' and args['issuer'][1:]==']')):
        issuer = args['issuer']
    else:
        return json.dumps({'success' : False, 'error' : 'The issuer provided was invalid.'})
    if args.has_key('reason') and args['reason'].__len__()<=500:
        reason = args['reason']
    else:
        return json.dumps({'success' : False, 'error' : 'The reason provided was invalid.'})
    if args.has_key('server') and args['server'].__len__()<=100:
        server = args['server']
    else: 
        return json.dumps({'success' : False, 'error' : 'The server provided was invalid.'})
    if db.session.query(Ban).filter(Ban.username==username).count() > 0:
        return json.dumps({'success' : False, 'error' : 'The user is already banned.'})
    ban = Ban(issuer, username, reason, server)
    db.session.add(ban)
    db.session.commit()
    return {'success' : True}

#@bans.route('/bans/local/delban.json')
def delban(request):
    args = request.args
    if args.has_key('username') and verifyusername(args['username']):
        username = args['username']
    else:
        return json.dumps({'success' : False, 'error' : 'The username provided was invalid'})
    num = db.sAession.query(Ban).filter(Ban.username==username).delete()
    db.session.commit()
    return {'success' : True, 'num' : num}

#@bans.route('/bans/local/getnotes.json')
def getlocalnotes(request):
    args = request.args
    if args.has_key('username') and verifyusername(args['username']):
        username = args['username']
    else:
        return json.dumps({'success' : False, 'error' : 'The username provided was invalid'})
    notes = db.session.query(Note).filter(Note.username==args['username'])
    count = notes.count()
    response = {'notecount' : count}
    if count > 0:
        response['notes'] = []
        for note in notes:
            retnote = {}
            retnote['uid'] = note.id
            retnote['issuer'] = note.issuer
            retnote['time'] = note.gettime()
            retnote['note'] = note.note
            retnote['server'] = note.server
            response['notes'].append(retnote)
    return response

#@bans.route('/bans/local/addnote.json')
def addnote(request):
    args = request.args
    if args.has_key('username') and verifyusername(args['username']):
        username = args['username']
    else:
        return json.dumps({'success' : False, 'error' : 'The username provided was invalid.'})
    if args.has_key('issuer') and (verifyusername(args['issuer']) or (args['issuer'][:1]=='[' and args['issuer'][1:]==']')):
        issuer = args['issuer']
    else:
        return json.dumps({'success' : False, 'error' : 'The issuer provided was invalid.'})
    if args.has_key('note') and args['note'].__len__()<=500:
        note = args['note']
    else:
        return json.dumps({'success' : False, 'error' : 'The note provided was invalid.'})
    if args.has_key('server') and args['server'].__len__()<=100:
        server = args['server']
    else:
        return json.dumps({'success' : False, 'error' : 'The server provided was invalid.'})
    note = Note(issuer, username, note, server)
    db.session.add(note)
    db.session.commit()
    return {'success' : True}

#@bans.route('/bans/local/delnote.json')
def delnote(request):
    args = request.args
    if args.has_key('id') and args['id'].isdigit():
        id = args['id']
    else:
        return json.dumps({'success' : False, 'error' : 'The provided integer id was invalid.'})
    num = db.session.query(Note).filter(Note.id==id).delete()
    db.session.commit()
    return {'success' : True, 'num' : num}

#@bans.route('/bans/local/fulllookup.json')
def fulllocallookup(request):
    args = request.args
    if args.has_key('username') and verifyusername(args['username']):
                username = args['username']
    else:
        return json.dumps({'success' : False, 'error' : 'The username provided was invalid'})
    bans = db.session.query(Ban).filter(Ban.username==args['username'])
    bancount = bans.count()
    notes = db.session.query(Note).filter(Note.username==args['username'])
    notecount = notes.count()
    response = {'notecount' : notecount, 'bancount' : bancount}

    if notecount > 0:
        response['notes'] = []
        for note in notes:
            retnote = {}
            retnote['uid'] = note.id
            retnote['issuer'] = note.issuer
            retnote['time'] = note.gettime()
            retnote['note'] = note.note
            retnote['server'] = note.server
            response['notes'].append(retnote)
    if bancount > 0:
        response['bans'] = []
        for ban in bans:
            retban = {}
            retban['uid'] = ban.id
            retban['issuer'] = ban.issuer
            retban['time'] = ban.gettime()
            retban['reason'] = ban.reason
            retban['server'] = ban.server
            response['bans'].append(retban)
    return response

#@bans.route('/bans/fulllookup.json')
def fullfulllookup(request):
    args = request.args
    if args.has_key('username') and verifyusername(args['username']):
                username = args['username']
    else:
        return json.dumps({'success' : False, 'error' : 'The username provided was invalid'})
    return mergedata([fulllocallookup(request), fullgloballookup(request)])

methods = {
    "local_getbans" : getlocalbans, 
    "local_getnotes" : getlocalnotes, 
    "local_lookup" : fulllocallookup, 
    "local_addnote" : addnote, 
    "local_addban" : addban,
    "local_delnote" : delnote, 
    "local_delban" : delban, 
    "global_getbans" : getglobalbans, 
    "global_getnotes" : getglobalnotes, 
    "global_lookup" : fullgloballookup, 
    "full_lookup" : fullfulllookup, 
    }

@bans.route('/bans/<string:method>.json')
#@login_required
def execute_method(method):
#    with Permission(RoleNeed('bans.%s' % method)).require(403):
    if method not in methods:
        abort(404)
    return json.dumps(methods[method](request))

