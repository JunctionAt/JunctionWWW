import requests

#If a feature is unsupported, return None


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
    response = {"bancount": 0, "bans": []}

    r = requests.get("http://minebans.com/feed/player_bans.json?player_name=%s" % (user,))
    if r.status_code != requests.codes.ok:
        return {"error": "HTTP ERROR: " + r.status_code}
    j = r.json
    for ban in j:
        convban = {'reason': "%s: %s" % (ban['reason'], ban['long_reason']), 'server': ban['server_name'],
                   'error': "HTTP ERROR: " + str(404)}
        response['bans'].append(convban)
        response['bancount'] += 1
    print response
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

