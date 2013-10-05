from flask import Flask, request
from reverse_proxied import ReverseProxied
from os import pathsep


# Setup App
application = Flask(__name__)

# Setup Extensions
ReverseProxied(application)

# Setup Jinja Env
application.jinja_env.add_extension('jinja2.ext.do')

from util import pretty_date
application.jinja_env.filters['pretty_date'] = pretty_date

# Load config files
with application.app_context():
    from config import local_config
    application.config.from_object(local_config)
    from config import blueprint_config
    application.config.from_object(blueprint_config)

# Setup blueprints from config
for blueprint in application.config["BLUEPRINTS"]:
    application.register_blueprint(**blueprint)

from blueprints import base

# Read the git hash from a file. This should be set by the deploy script
try:
    with open('version_hash', 'r') as version_file:
        application.config['version_hash'] = version_file.readline()
except IOError:
    application.config['version_hash'] = "DEVELOP"

# Setup exceptional
#if application.config.has_key("EXCEPTIONAL_API_KEY"):
#    from flask.ext.exceptional import Exceptional
#    exceptional = Exceptional(application)

# Setup airbrake/errbit
if application.config.get('AIRBRAKE_ENABLED', True):
    with application.app_context():
        from airbrake import AirbrakeErrorHandler
        from flask.signals import got_request_exception
        from flask import current_app

        def log_exception(sender, exception, **extra):
            print "yee"
            handler = AirbrakeErrorHandler(
                api_key=application.config['AIRBRAKE_API_KEY'],
                api_url=application.config['AIRBRAKE_API_URL'], #"http://errbit.junction.at/notifier_api/v2/notices",
                env_name=application.config['version_hash'],
                request_url=request.url,
                request_path=request.path,
                request_method=request.method,
                request_args=request.args,
                request_headers=request.headers)
            handler.emit(exception)

        got_request_exception.connect(log_exception, current_app)

# Error page
@application.errorhandler(500)
def internal_error(error):
    #handler = AirbrakeErrorHandler(
    #    api_key="97ed9107d2d204537f07080f85315281",
    #    api_url="http://errbit.junction.at/notifier_api/v2/notices",
    #    env_name=application.config['version_hash'],
    #    request_url=request.url,
    #    request_path=request.path,
    #    request_method=request.method,
    #    request_args=request.args,
    #    request_headers=request.headers)
    #handler.emit(error)

    return "Something went wrong. :( Staff have been notified, and are working on the issue. Please check back later.", 500

# Load debug stuffs
if application.config['DEBUG']:
    with application.app_context():
        import debug
        debug.setup_env()

# If the app was started directly, run http server
def run():
    application.run(
        host=application.config.get('HOST', None),
        port=application.config.get('PORT', None),
        use_evalex=False)