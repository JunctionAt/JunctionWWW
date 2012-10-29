import time
import requests

#If a feature is unsupported, return None

apikey = '9eadd4b46859e9b54a93880e9e3506dd'

def getbans(user):
    """ 
    Should return a dict containing info about the user.
    It should contain the following info:
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
    response = {"bancount" : 0, "bans" : []}

    r = requests.get("http://www.mcbouncer.com/api/getBans/9eadd4b46859e9b54a93880e9e3506dd/%s/0/-1" % (user,))
    j = r.json
    for ban in j['data']:
        convban = {}
        convban['reason'] = ban['reason']
        convban['server'] = ban['server']
        convban['issuer'] = ban['issuer']
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

