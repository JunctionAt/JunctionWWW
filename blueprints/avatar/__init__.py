import flask
import md5
import urllib

class Blueprint(flask.Blueprint):
    
    @staticmethod
    def avatar(mail):
        _mail = mail or ""
        hash = md5.new(_mail).hexdigest().lower()
        link = "http://www.gravatar.com/%s"%hash if _mail else None
        img = "https://www.gravatar.com/avatar/%s.png?r=pg&d=retro"%hash
        return type('Avatar', (object, ), {
                "link": link,
                "small": "%s&s=32"%img,
                "medium": "%s&s=64"%img,
                "large": "%s&s=128"%img,
                "portrait": "%s&s=256"%img
                })

avatar = Blueprint('avatar', __name__)
