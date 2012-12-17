from flask import Blueprint, render_template, url_for
#from flask.ext.browserid import BrowserID
import os
import time

blueprint = Blueprint('forum', __name__, template_folder='templates')
# Secret key can change with each new version this forces all old logins to expire :)

# Import here so database it can reach the app object.
#from database.login import get_user, get_user_by_id

# Now the actual login system
#browser_id = BrowserID()
#browser_id.user_loader(get_user)
#browser_id.init_app(app)

@blueprint.route("/forum/servertime")
def time_at_server():
    """Generic default testy route. Handy for debugging."""
    return time.asctime()

#@blueprint.route("/google980b6417f3302651.html")
#def google_auth():
#    return render_template("google980b6417f3302651.html")

@blueprint.route("/forum/")
def index():
    """Proper index function."""
    return render_template("index.html")

# Import application views here!
import views.board
import views.index
import views.topic
import views.reply

# All routes have now been registered.

# Setup logging
#from custom_super_mega_non_blocking_logger import ThreadedTlsSMTPHandler
#from config import email_password

ADMINS = ["jkbbwr@gmail.com"]
#if not app.debug:
#    import logging
#    mail_handler = ThreadedTlsSMTPHandler(("smtp.gmail.com", 587), 'admin@pythonforum.org', ADMINS,
#        'Error happened!', ('admin@python-forum.org', email_password))
#    mail_handler.setLevel(logging.ERROR)
#    app.logger.addHandler(mail_handler)
