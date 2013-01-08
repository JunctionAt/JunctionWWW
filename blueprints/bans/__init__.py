import flask
import re
import json
import Queue
from threading import Thread
from flask import Blueprint, abort, request
from flask_login import current_user
from flask.ext.principal import Permission, RoleNeed
from blueprints.auth import login_required
from blueprints.base import mongo
from systems import minebans, mcbans, mcbouncer
from ban_model import Ban, Note

#Todo: Add authentication!

username_regex = re.compile('^[a-zA-Z0-9_]+$')
ban_systems = {"minebans" : minebans, "mcbans" : mcbans, "mcbouncer" : mcbouncer}
bans = Blueprint('bans', __name__, template_folder="templates")

#db.create_all()

def verify_username(username):
    return len(username)<=16 and username_regex.match(username)

#This method takes care of merging responses in a proper way
def merge_data(ret_list):
    response = {}
    for ret in ret_list:
        if ret == None:
            continue
        system_name = ''
        if '_sysname' in ret:
            system_name = ret['_sysname']
        if 'bans' in ret and len(ret['bans'])!=0:
            if 'bans' not in response:
                response['bans'] = []
            if 'bancount' not in response:
                response['bancount'] = 0
            for ban in ret['bans']:
                if system_name is not None:
                    ban['system'] = system_name
                response['bans'].append(ban)
                response['bancount'] += 1
        if 'notes' in ret and len(ret['notes'])!=0:
            if 'notes' not in response:
                response['notes'] = []
            if 'notecount' not in response:
                response['notecount'] = 0
            for note in ret['notes']:
                if system_name is not None:
                    note['system'] = system_name
                response['notes'].append(note)
                response['notecount'] += 1
        if ('errors' in ret and len(ret['errors'])!=0) or ('error' in ret):
            if 'errors' not in response:
                response['errors'] = []
            if 'error' in ret:
                if(isinstance(ret['error'], str)):
                    response['errors'].append({"system" : system_name, "error" : ret['error']})
                elif(isinstance(ret['error'], dict)):
                    error = ret['error']
                    if system_name is not None:
                        error['system'] = system_name
                    response['errors'].append(error)
            if 'errors' in ret and len(ret['errors'])!=0:
                for error in ret['errors']:
                    if(isinstance(error, str)):
                        response['errors'].append({"system" : system_name, "error" : error})
                    elif(isinstance(error, dict)):
                        if system_name is not None:
                            error['system'] = system_name
                        response['errors'].append(error)
    return response

class ReqThread(Thread):
    def __init__(self, func, queue, system_name):
        Thread.__init__(self)
        self.func = func
        self.return_queue = queue
        self.system_name = system_name

    def run(self):
        ret = self.func()
        if ret != None:
            ret['_sysname'] = self.system_name
        self.return_queue.put(ret)

#GLOBAL

#@bans.route('/bans/global/getbans.json')
def get_global_bans(request):
    args = request.args
    if args.has_key('username') and verify_username(args['username']):
        username = args['username']
    else:
        return {'success' : False, 'error' : 'The username provided was invalid'}
    return_queue = Queue.Queue()
    threads = []
    for key, value in ban_systems.items():
        t = ReqThread(lambda: value.getbans(username), return_queue, key)
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

    return merge_data(list(return_queue.queue))

#@bans.route('/bans/global/getnotes.json')
def get_global_notes(request):
    args = request.args
    if args.has_key('username') and verify_username(args['username']):
        username = args['username']
    else:
        return {'success' : False, 'error' : 'The username provided was invalid'}
    return_queue = Queue.Queue()
    threads = []
    for key, value in ban_systems.items():
        t = ReqThread(lambda: value.getnotes(username), return_queue, key)
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

    return merge_data(list(return_queue.queue))

#@bans.route('/bans/global/fulllookup.json')
def full_global_lookup(request):
    args = request.args
    if args.has_key('username') and verify_username(args['username']):
        username = args['username']
    else:
        return {'success' : False, 'error' : 'The username provided was invalid'}
    return_queue = Queue.Queue()
    threads = []
    for key, value in ban_systems.items():
        t = ReqThread(lambda: value.getnotes(username), return_queue, key)
        t.start()
        threads.append(t)
        t = ReqThread(lambda: value.getbans(username), return_queue, key)
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

    return merge_data(list(return_queue.queue))

#LOCAL

#@bans.route('/bans/local/getbans.json')
def get_local_bans(request):
    args = request.args
    if args.has_key('username') and verify_username(args['username']):
        username = args['username']
    else:
        return {'success' : False, 'error' : 'The username provided was invalid'}
    bans = Ban.objects(username=args['username'], active=True)
    count = len(bans)
    response = {'bancount' : count}
    if count > 0:
        response['bans'] = []
        for ban in bans:
            retban = {}
            retban['uid'] = ban.uid
            retban['issuer'] = ban.issuer
            retban['time'] = ban.get_time()
            retban['reason'] = ban.reason
            retban['server'] = ban.server
            response['bans'].append(retban)
    print response
    return response

#@bans.route('/bans/local/banuser.json')
def add_ban(request):
    args = request.args
    if args.has_key('username') and verify_username(args['username']):
        username = args['username']
    else:
        return {'success' : False, 'error' : 'The username provided was invalid.'}
#    if args.has_key('issuer') and (verifyusername(args['issuer']) or (args['issuer'][:1]=='[' and args['issuer'][1:]==']')):
#        issuer = args['issuer']
#    else:
#        return {'success' : False, 'error' : 'The issuer provided was invalid.'}
    if args.has_key('issuer') and verify_username(args['issuer']):
        issuer = args['issuer']
    else:
        return {'success' : False, 'error' : 'The issuer provided was invalid.'}
    if args.has_key('reason') and args['reason'].__len__()<=500:
        reason = args['reason']
    else:
        return {'success' : False, 'error' : 'The reason provided was invalid.'}
    if args.has_key('server') and args['server'].__len__()<=100:
        server = args['server']
    else: 
        return {'success' : False, 'error' : 'The server provided was invalid.'}
    if len(Ban.objects(username=username, active=True)) > 0:
        return {'success' : False, 'error' : 'The user is already banned.'}
    Ban(issuer=issuer, username=username, reason=reason, server=server).save()
    return {'success' : True}

#@bans.route('/bans/local/delban.json')
def del_ban(request):
    args = request.args
    if args.has_key('username') and verify_username(args['username']):
        username = args['username']
    else:
        return {'success' : False, 'error' : 'The username provided was invalid'}
#    ban = db.session.query(Ban).filter(Ban.username==username).first()
#    if ban != None:
#        db.session.add(RemovedBan(ban, current_user.name))
    banmatch = Ban.objects(username=username, active=True)
    if len(banmatch)==0:
        return {'success' : False}
    banmatch.first().update(set__active=False)
    return {'success' : True, 'num' : 1}

#@bans.route('/bans/local/getnotes.json')
def get_local_notes(request):
    args = request.args
    if args.has_key('username') and verify_username(args['username']):
        username = args['username']
    else:
        return {'success' : False, 'error' : 'The username provided was invalid'}
    notes = Note.objects(username=args['username'], active=True)
    count = len(notes)
    response = {'notecount' : count}
    if count > 0:
        response['notes'] = []
        for note in notes:
            return_note = {}
            return_note['uid'] = note.uid
            return_note['issuer'] = note.issuer
            return_note['time'] = note.get_time()
            return_note['note'] = note.note
            return_note['server'] = note.server
            response['notes'].append(return_note)
    return response

#@bans.route('/bans/local/addnote.json')
def add_note(request):
    args = request.args
    if args.has_key('username') and verify_username(args['username']):
        username = args['username']
    else:
        return {'success' : False, 'error' : 'The username provided was invalid.'}
    if args.has_key('issuer') and verify_username(args['issuer']):
        issuer = args['issuer']
    else:
        return {'success' : False, 'error' : 'The issuer provided was invalid.'}
    if args.has_key('note') and args['note'].__len__()<=500:
        note = args['note']
    else:
        return {'success' : False, 'error' : 'The note provided was invalid.'}
    if args.has_key('server') and args['server'].__len__()<=100:
        server = args['server']
    else:
        return {'success' : False, 'error' : 'The server provided was invalid.'}

    Note(issuer=issuer, username=username, note=note, server=server).save()
    return {'success' : True}

#@bans.route('/bans/local/delnote.json')
def del_note(request):
    args = request.args
    if args.has_key('id') and args['id'].isdigit():
        id = args['id']
    else:
        return {'success' : False, 'error' : 'The provided integer id was invalid.'}
    note = Note.objects(id=id, active=True).first().update(active=False)
    return {'success' : True, 'num' : 1}

#@bans.route('/bans/local/fulllookup.json')
def full_local_lookup(request):
    args = request.args
    if args.has_key('username') and verify_username(args['username']):
                username = args['username']
    else:
        return {'success' : False, 'error' : 'The username provided was invalid'}
    bans = Ban.objects(username=args['username'], active=True)
    ban_count = len(bans)
    notes = Note.objects(username=args['username'], active=True)
    notecount = notes.count()
    response = {'notecount' : notecount, 'bancount' : ban_count}

    if notecount > 0:
        response['notes'] = []
        for note in notes:
            return_note = {}
            return_note['uid'] = note.uid
            return_note['issuer'] = note.issuer
            return_note['time'] = note.get_time()
            return_note['note'] = note.note
            return_note['server'] = note.server
            response['notes'].append(return_note)
    if ban_count > 0:
        response['bans'] = []
        for ban in bans:
            return_ban = {}
            return_ban['uid'] = ban.uid
            return_ban['issuer'] = ban.issuer
            return_ban['time'] = ban.get_time()
            return_ban['reason'] = ban.reason
            return_ban['server'] = ban.server
            response['bans'].append(return_ban)
    return response

#@bans.route('/bans/fulllookup.json')
def full_full_lookup(request):
    args = request.args
    if args.has_key('username') and verify_username(args['username']):
                username = args['username']
    else:
        return {'success' : False, 'error' : 'The username provided was invalid'}
    return merge_data([full_local_lookup(request), full_global_lookup(request)])

methods = {
    "local_getbans" : get_local_bans, 
    "local_getnotes" : get_local_notes, 
    "local_lookup" : full_local_lookup,
    "local_addnote" : add_note,
    "local_addban" : add_ban,
    "local_delnote" : del_note,
    "local_delban" : del_ban, 
    "global_getbans" : get_global_bans, 
    "global_getnotes" : get_global_notes, 
    "global_lookup" : full_global_lookup, 
    "full_lookup" : full_full_lookup,
    }

@bans.route('/bans/<string:method>.json')
@login_required
def execute_method(method):
    with Permission(RoleNeed('bans.%s' % method)).require(403):
        if method not in methods:
            abort(404)
        result = methods[method](request)
        if(not result.has_key('success')):
            result['success'] = True
        return json.dumps(result)
