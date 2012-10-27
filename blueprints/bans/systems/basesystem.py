
def getbans(user):
    """ 
    Should return a dict containing info about the user.
    It should contain the following info:
      -   int : bancount
      - O string : error - if this is returned, it is fine to not return anything else
      - O array : bans
          -   dict - info about the ban
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
              - O string : issuer
              - O string : reason
              - O string : server
          -   ...
    """

def fulllookup(user):
    """
    Should return a dict containing info about the user.
    It should be containing the following info:
      -   int : bancount
      - O string : error - if this is returned, it is fine to not return anything else
      - O array : bans
          -   dict - info about the ban
              - O string : issuer
              - O string : reason
              - O string : server
          -   ...  
      - O int : playerrep - 0-10, the higher the better
      - O array : altlist
          -   dict - info about the alt
              -   string : username
              - O int : playerrep
          -   ...
    """
    return {"bancount" : 0}

