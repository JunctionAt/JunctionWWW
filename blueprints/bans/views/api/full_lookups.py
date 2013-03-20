__author__ = 'HansiHE'

from . import verify_username, merge_data
from local_lookups import full_local_lookup
from global_lookups import full_global_lookup

#@bans.route('/bans/fulllookup.json')
def full_full_lookup(request):
    args = request.args
    if args.has_key('username') and verify_username(args['username']):
        username = args['username']
    else:
        return {'success' : False, 'error' : 'The username provided was invalid'}
    return merge_data([full_local_lookup(request), full_global_lookup(request)])