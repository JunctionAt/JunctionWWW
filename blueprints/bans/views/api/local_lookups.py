__author__ = 'HansiHE'

import re
from . import verify_username
from ...ban_model import Ban, Note

#@bans.route('/bans/local/fulllookup.json')
def full_local_lookup(request):
    args = request.args
    if args.has_key('username') and verify_username(args['username']):
        username = args['username']
    else:
        return {'success' : False, 'error' : 'The username provided was invalid'}
    username_regexified = re.compile(args['username'], re.IGNORECASE)
    bans = Ban.objects(username=username_regexified, active=True)
    ban_count = len(bans)
    notes = Note.objects(username=username_regexified, active=True)
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