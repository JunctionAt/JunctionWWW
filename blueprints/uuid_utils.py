# Shamelessly stolen from https://github.com/Thezomg/mcapi/

## Based on Java from https://github.com/Mojang/AccountsClient/
from flask.ext.restful.reqparse import Argument

import requests
import json
from requests.exceptions import ConnectionError

AGENT = "minecraft"
PROFILE_URL = "https://api.mojang.com/profiles/page/{page}"
UUID_PROFILE_URL = 'https://sessionserver.mojang.com/session/minecraft/profile/{uuid}'


class NoSuchUserException(Exception): pass


class ProfileCriteria(dict):
    def __init__(self, name, agent):
        self['name'] = name
        self['agent'] = agent


def get_profile(uuid, timeout=10):
    url = UUID_PROFILE_URL.format(uuid=uuid)
    try:
        r = requests.get(url, timeout=timeout)
        profile = r.json()
    except:
        profile = None

    return profile


def get_uuid(*name, **kwargs):
    timeout = 10
    if "timeout" in kwargs:
        timeout = kwargs["timeout"]
    if len(name) == 0:
        return None
    crit = [ProfileCriteria(x, AGENT) for x in name]
    p = []

    page = 1
    while True:
        url = PROFILE_URL.format(page=page)
        data = json.dumps(crit)
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        r = requests.post(url, data=data, headers=headers, timeout=timeout)
        profiles = r.json()
        if 'profiles' in profiles:
            if profiles['size'] == 0:
                break
            p.extend(profiles['profiles'])

        page += 1
                
    return p

def lookup_uuid(username):
    res = get_uuid(username)
    if not res:
        raise ConnectionError()
    for result in res:
        if result.get(u"name", None).lower() == username.lower():
            return result.get(u"id", None)
    raise NoSuchUserException("no user exists with the username '%s'" % username)

def lookup_uuid_name(username):
    res = get_uuid(username)
    if not res:
        raise ConnectionError()
    for result in res:
        if result.get(u"name", None).lower() == username.lower():
            return result.get(u"id", None), result.get(u"name")
    raise NoSuchUserException("no user exists with the username '%s'" % username)

def lookup_name(uuid):
    res = get_profile(uuid)
    if not res:
        raise ConnectionError()
    if not res.get(u'name'):
        raise NoSuchUserException("no user exists with the uuid '%s'" % uuid)
    return res.get(u'name')

def validate_uuid(uuid):
    if len(uuid) != 32:
        return False
    try:
        int(uuid, 16)
    except ValueError:
        return False
    return True

def uuid_type(value):
    if not validate_uuid(value):
        raise TypeError("'%s' is not a valid uuid" % value)
    return value