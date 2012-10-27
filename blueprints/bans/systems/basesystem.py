
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
    return {"bancount" : 0}

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
    return {"bancount" : 0}

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
    return {"notecount" : 0}

def fulllookup(user):
    """
    Should return a dict containing info about the user.
    It should be containing the following info:
      -   int : bancount
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
      -   int : altcount
      - O array : altlist
          -   dict - info about the alt
              -   string : username
              - O string : uid
              - O int : playerrep
          -   ...
      -   int : notecount
      - O array : notelist
          -   dict - note
              - O string : uid
              - O string : issuer
              - O string : server
              - O string : note
          -   ...
    """
    return {"bancount" : 0, "altcount" : 0, "notecount" : 0}

