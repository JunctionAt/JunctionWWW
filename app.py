from flask import Flask
from reverse_proxied import ReverseProxied
from flask.ext.admin import Admin

application = Flask(__name__)

application.secret_key = "WeAOcOqFruPTsb6bXKNU"

application.config.from_object("local_config")

with application.app_context():
    application.config.from_object("config")

for blueprint in application.config["BLUEPRINTS"]:
    application.register_blueprint(**blueprint)

ReverseProxied(application)
    
if application.config['DEBUG']:
	from werkzeug import SharedDataMiddleware
	import os
	application.wsgi_app = SharedDataMiddleware(application.wsgi_app, {
	  '/': os.path.join(os.path.dirname(__file__), 'static')
	})

def run():
    application.run(
        host=application.config.get('HOST', None),
        port=application.config.get('PORT', None),
        use_evalex=False)

if __name__ == "__main__": run()
