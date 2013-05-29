from flask import Flask
from reverse_proxied import ReverseProxied
from flask.ext.admin import Admin

application = Flask(__name__)

application.secret_key = "3750vIhza0IdTjPlI2H612cI8vQvfxIP7B4lsE5L"
application.config.from_object("local_config")

application.jinja_env.add_extension('jinja2.ext.do')

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

    application.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
    application.config["DEBUG_TB_PROFILER_ENABLED"] = False
    application.config['DEBUG_TB_PANELS'] = (
        'flask_debugtoolbar.panels.headers.HeaderDebugPanel',
        'flask_debugtoolbar.panels.logger.LoggingPanel',
        'flask_debugtoolbar.panels.timer.TimerDebugPanel',
        'flask_debugtoolbar.panels.profiler.ProfilerDebugPanel',
        'flask_debugtoolbar.panels.request_vars.RequestVarsDebugPanel',
        #'flask_debugtoolbar.panels.template.TemplateDebugPanel',
        #'flask_debugtoolbar.panels.versions.VersionDebugPanel',
        'flask_debugtoolbar_mongo.panel.MongoDebugPanel',
    )

    from flask_debugtoolbar import DebugToolbarExtension
    #toolbar = DebugToolbarExtension(application)
#else:
#    import logging
#    from logging.handlers import TimedRotatingFileHandler
#    handler = TimedRotatingFileHandler('log/log', when='D', interval=1, utc=True)
#    handler.setLevel(logging.WARNING)
#    application.logger.addHandler(handler)

if application.config.has_key("EXCEPTIONAL_API_KEY"):
    from flask.ext.exceptional import Exceptional
    exceptional = Exceptional(application)

def run():
    application.run(
        host=application.config.get('HOST', None),
        port=application.config.get('PORT', None),
        use_evalex=False)

if __name__ == "__main__": run()
