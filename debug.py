from flask import current_app as application


def setup_env():

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
        # 'flask_debugtoolbar.panels.template.TemplateDebugPanel',
        # 'flask_debugtoolbar.panels.versions.VersionDebugPanel',
        'flask_mongoengine.panels.MongoDebugPanel')

    from flask_debugtoolbar import DebugToolbarExtension
    toolbar = DebugToolbarExtension(application)
