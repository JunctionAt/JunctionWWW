from flask import Flask, render_template
from werkzeug.utils import import_string

application = Flask(__name__, template_folder="templates")
application.config.from_object("config")

# let $APP_SETTINGS be a path to a local config file
try:
    application.config.from_object("local_config")
except ImportError:
    """No worries bro"""

for blueprint in application.config["BLUEPRINTS"]:
    application.register_blueprint(**blueprint)
