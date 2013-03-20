__author__ = 'HansiHE'

import re
from threading import Thread
from ...systems import minebans, mcbans, mcbouncer
from ... import bans
from blueprints.auth import login_required
from flask_login import current_user
from flask import abort, request
import json

username_regex = re.compile('^[a-zA-Z0-9_]+$')
ban_systems = {"minebans" : minebans, "mcbans" : mcbans, "mcbouncer" : mcbouncer}

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


import global_notes
import global_bans
import global_lookups
import local_notes
import local_bans
import local_lookups
import full_lookups

methods = {
    "local_getbans" : local_bans.get_local_bans,
    "local_getnotes" : local_notes.get_local_notes,
    "local_lookup" : local_lookups.full_local_lookup,
    "local_addnote" : local_notes.add_note,
    "local_addban" : local_bans.add_ban,
    "local_delnote" : local_notes.del_note,
    "local_delban" : local_bans.del_ban,
    "global_getbans" : global_bans.get_global_bans,
    "global_getnotes" : global_notes.get_global_notes,
    "global_lookup" : global_lookups.full_global_lookup,
    "full_lookup" : full_lookups.full_full_lookup,
    }

@bans.route('/bans/<string:method>.json')
@login_required
def execute_method(method):
    if method not in methods:
        abort(404)
    if not current_user.has_permission("bans.api.%s" % method):
        abort(403)
    result = methods[method](request)
    if(not result.has_key('success')):
        result['success'] = True
    return json.dumps(result)