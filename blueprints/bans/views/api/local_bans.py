__author__ = 'HansiHE'

import re
from ...ban_model import Ban
from . import verify_username
from datetime import datetime

#@bans.route('/bans/local/getbans.json')
def get_local_bans(request):
    args = request.args
    if args.has_key('username') and verify_username(args['username']):
        username = args['username']
    else:
        return {'success' : False, 'error' : 'The username provided was invalid'}
    bans = Ban.objects(username=re.compile(args['username'], re.IGNORECASE), active=True)
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
    if args.has_key('remover') and verify_username(args['remover']):
        remover = args['username']
    else:
        return {'success' : False, 'error' : 'The remover provided was invalid'}
    #    ban = db.session.query(Ban).filter(Ban.username==username).first()
    #    if ban != None:
    #        db.session.add(RemovedBan(ban, current_user.name))
    banmatch = Ban.objects(username=re.compile(username, re.IGNORECASE), active=True).first()
    if banmatch is None:
        return {'success' : False}
    banmatch.active = False
    banmatch.removal_time = datetime.utcnow()
    banmatch.remover = remover
    banmatch.save()
    return {'success' : True, 'num' : 1}