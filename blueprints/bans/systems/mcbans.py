import requests
import json
import sys

#If a feature is unsupported, return None

apikey = '205b3fa7a5aae89e6913c5c5bcbe7c50b1b0cfd1'

def getbans(user):
    """ 
    Should return a dict containing info about the user.
    It should contain the following info:
      -   int : bancount
      - O int : playerrep
      - O string : error - if this is returned, it is fine to not return anything else
      - O array : bans
          -   dict - info about the ban
              - O string : uid
              - O string : issuer
              - O string : reason
              - O string : server	
          -   ...
    """
    response = {"bancount" : 0, "bans" : []}

    payload = {"player" : user, "admin" : "[backend]", "exec" : "playerLookup"}
    r = requests.post("http://api.mcbans.com/v2/%s" % (apikey,), data=payload)
    #print(r.text)
    j = r.json
    if j is None or not j.has_key('global'):
        #print(":(")
        return response
    for ban in j['global']:
        convban = {}
        splitted = ban.split(" .:. ")
        convban['reason'] = splitted[1]
        convban['server'] = splitted[0]
        response['bans'].append(convban)
        response['bancount'] += 1
    return response

def getipbans(ip):
    """
    Should return a dict containing info about the ip.
    If this is not supported by the system, just return.
      -   int : bancount
      - O string : error - if this is returned, it is fine to not return anything else
      - O array : bans
          -   dict - info about the ban
              - O string : uid
              - O string : issuer
              - O string : reason
              - O string : server
          -   ...
    """
    return None

def getnotes(user):
    """
    Should return a dict containing notes for the user.
    It should be containing the following info:
      -   int : notecount
      - O string : uid
      - O string : error - if this is returned, it is fine to not return anything else
      - O array : notelist
          -   dict - note
              - O string : uid
              - O string : issuer
              - O string : server
              - O string : note
          -   ...
    """
    return None

def fulllookup(user):
    """
    Should return a dict containing info about the user.
    It should be containing the following info:
      -   int : bancount - None if unsupported
      - O string : uid
      - O int : playerrep - 0-10, the higher the better
      - O string : error - if this is returned, it is fine to not return anything else
      - O array : bans
          -   dict - info about the ban
              - O string : uid
              - O string : issuer
              - O string : reason
              - O string : server
          -   ...  
      -   int : altcount - None if unsupported
      - O array : altlist
          -   dict - info about the alt
              -   string : username
              - O string : uid
              - O int : playerrep
          -   ...
      -   int : notecount - None if unsupported
      - O array : notelist
          -   dict - note
              - O string : uid
              - O string : issuer
              - O string : server
              - O string : note
          -   ...
    """
    return {"bancount" : 0, "altcount" : None, "notecount" : None}

