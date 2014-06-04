from werkzeug.exceptions import ClientDisconnected

from flask import Flask, request
from flask import current_app
from flask_cache import Cache
from mongoengine import connect
from flask_superadmin import Admin
from flask_mail import Mail
from flaskext.markdown import Markdown
from flask_restful import Api

from reverse_proxied import ReverseProxied
from assets import assets


class ExtensionAccessObject(object):
    def __init__(self):
        self.cache = Cache(current_app, config={'CACHE_TYPE': 'simple'})
        self.mongo = connect(current_app.config["MONGO_DB"])
        self.mail = Mail(current_app)
        self.admin = Admin(current_app)
        self.rest_api = Api(current_app, prefix="/api")
        self.markdown = Markdown(current_app, safe_mode="escape")
        self.assets = assets(current_app)


def construct_application(config_override=None):
    # Setup App
    application = Flask(__name__)

    # Setup Extensions
    ReverseProxied(application)

    # Setup Jinja Env
    application.jinja_env.add_extension('jinja2.ext.do')

    from util import pretty_date_since, full_date
    application.jinja_env.filters['pretty_date'] = pretty_date_since
    application.jinja_env.filters['full_date'] = full_date

    # Load local_config
    with application.app_context():
        from config import local_config
        application.config.from_object(local_config)
        application.config.from_object(config_override)

    with application.app_context():
        application.extension_access_object = ExtensionAccessObject()

    # Load blueprints files
    with application.app_context():
        from config import blueprint_config
        application.config.from_object(blueprint_config)

    # Setup blueprints from config
    for blueprint in application.config["BLUEPRINTS"]:  # TODO: Find a way to replace this, its shit
        application.register_blueprint(**blueprint)

    # Read the git hash from a file. This should be set by the deploy script
    try:
        with open('version_hash', 'r') as version_file:
            application.config['version_hash'] = version_file.readline()
    except IOError:
        application.config['version_hash'] = "DEVELOP"

    # Setup airbrake/errbit
    if application.config.get('AIRBRAKE_ENABLED', True):
        from airbrake import AirbrakeErrorHandler
        from flask.signals import got_request_exception

        @got_request_exception.connect_via(application)
        def log_exception(sender, exception, **extra):
            if isinstance(exception, (ClientDisconnected, )):
                return
            handler = AirbrakeErrorHandler(
                api_key=application.config['AIRBRAKE_API_KEY'],
                api_url=application.config['AIRBRAKE_API_URL'],
                env_name=application.config['version_hash'],
                env_variables={'type': 'caught'},
                request_url=request.url,
                request_path=request.path,
                request_method=request.method,
                request_args=request.args,
                request_headers=request.headers)
            handler.emit(exception)

        def log_error(exception):
            handler = AirbrakeErrorHandler(
                api_key=application.config['AIRBRAKE_API_KEY'],
                api_url=application.config['AIRBRAKE_API_URL'],
                env_name=application.config['version_hash'],
                env_variables={'type': 'logged'},
                request_url=request.url,
                request_path=request.path,
                request_method=request.method,
                request_args=request.args,
                request_headers=request.headers)
            handler.emit(exception)
        application.log_error = log_error
    else:
        def dummy_log_error(exception):
            print(exception)
        application.log_error = dummy_log_error

    # Load debug stuffs
    if application.config['DEBUG']:
        with application.app_context():
            import debug
            debug.setup_env()

    return application
