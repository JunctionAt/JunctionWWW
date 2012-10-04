"""Avatar support for objects with a mail string field"""

import flask
import md5
import urllib

class Blueprint(flask.Blueprint):
    
    @staticmethod
    def avatar(mail):
        default_email = "admin@junction.at"
        _mail = mail or default_email
        hash = md5.new(_mail).hexdigest().lower()
        link = "http://www.gravatar.com/%s"%hash if _mail else None
        default = urllib.quote("https://www.gravatar.com/avatar/%s.png?s="%md5.new(default_email).hexdigest().lower())
        img = ("https://www.gravatar.com/avatar/%s.png?r=pg&d="%hash)+default
        return type('Avatar', (object, ), dict(
                link=link,
                small="%s%d&s=%d"%(img,32,32),
                medium="%s%d&s=%d"%(img,64,64),
                large="%s%d&s=%d"%(img,128,128),
                portrait="%s%d&s=%d"%(img,256,256)))

avatar = Blueprint('avatar', __name__)
