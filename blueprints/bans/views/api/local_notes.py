__author__ = 'HansiHE'

import re
from ...ban_model import Note
from . import verify_username

#@bans.route('/bans/local/getnotes.json')
def get_local_notes(request):
    args = request.args
    if args.has_key('username') and verify_username(args['username']):
        username = args['username']
    else:
        return {'success' : False, 'error' : 'The username provided was invalid'}
    notes = Note.objects(username=re.compile(args['username'], re.IGNORECASE), active=True)
    count = len(notes)
    response = {'notecount' : count}
    if count > 0:
        response['notes'] = []
        for note in notes:
            return_note = {'uid': note.uid, 'issuer': note.issuer, 'time': note.get_time(), 'note': note.note,
                           'server': note.server}
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
        # noinspection PyShadowingBuiltins
        id = args['id']
    else:
        return {'success' : False, 'error' : 'The provided integer id was invalid.'}
    note = Note.objects(id=id, active=True).first().update(active=False)
    return {'success' : True, 'num' : 1}