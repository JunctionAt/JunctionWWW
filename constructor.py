__author__ = 'hansihe'

from flask import Flask, request
from flask import current_app
from flask.ext.cache import Cache
from mongoengine import connect
from flask.ext.superadmin import Admin
from flask.ext.mail import Mail
from flaskext.markdown import Markdown
from flask_restful import Api

from reverse_proxied import ReverseProxied
from assets import assets


class ExtensionAccessObject(object):
    def __init__(self):
        self.cache = Cache(current_app, config={'CACHE_TYPE': 'simple'})
        self.mongo = connect("pf")
        self.mail = Mail(current_app)
        self.admin = Admin(current_app)
        self.rest_api = Api(current_app, prefix="/api")
        self.markdown = Markdown(current_app, safe_mode="escape")
        self.assets = assets(current_app)


def construct_application():
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

        def log_exception(sender, exception, **extra):
            handler = AirbrakeErrorHandler(
                api_key=application.config['AIRBRAKE_API_KEY'],
                api_url=application.config['AIRBRAKE_API_URL'],
                env_name=application.config['version_hash'],
                request_url=request.url,
                request_path=request.path,
                request_method=request.method,
                request_args=request.args,
                request_headers=request.headers)
            handler.emit(exception)
        got_request_exception.connect(log_exception, sender=application)

    # Load debug stuffs
    if application.config['DEBUG']:
        with application.app_context():
            import debug
            debug.setup_env()

    return application