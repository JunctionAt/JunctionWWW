__author__ = 'HansiHE'

from . import verify_username, ban_systems, ReqThread, merge_data
import Queue

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