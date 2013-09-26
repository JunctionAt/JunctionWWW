from flask import Flask, request
from reverse_proxied import ReverseProxied
from flask.ext.restful import Api as Restful_Api


# Setup App
application = Flask(__name__)

# Setup Extensions
ReverseProxied(application)
rest_api = Restful_Api(application, prefix="/api")
application.rest_api = rest_api

# Setup Jinja Env
application.jinja_env.add_extension('jinja2.ext.do')

from util import pretty_date
application.jinja_env.filters['pretty_date'] = pretty_date

# Set secret key
# TODO: Move to local config
application.secret_key = "3750vIhza0IdTjPlI2H612cI8vQvfxIP7B4lsE5L"

# Load config files
with application.app_context():
    application.config.from_object("local_config")
    application.config.from_object("config")

# Setup blueprints from config
for blueprint in application.config["BLUEPRINTS"]:
    application.register_blueprint(**blueprint)

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
from airbrake import AirbrakeErrorHandler
import gevent
@application.errorhandler(500)
def internal_error(error):
    handler = AirbrakeErrorHandler(
        api_key="97ed9107d2d204537f07080f85315281",
        api_url="http://errbit.junction.at/notifier_api/v2/notices",
        env_name=application.config['version_hash'],
        request_url=request.url,
        request_path=request.path,
        request_method=request.method,
        request_args=request.args,
        request_headers=request.headers)
    #gevent.spawn(handler.emit, error)
    handler.emit(error)

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

if __name__ == "__main__": run()
