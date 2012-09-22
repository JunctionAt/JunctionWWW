from flask import Flask, render_template
from werkzeug.utils import import_string

application = Flask(__name__, template_folder="templates")
application.config.from_object("local_config")
application.config.from_object("config")

for blueprint in application.config["BLUEPRINTS"]:
    application.register_blueprint(**blueprint)
