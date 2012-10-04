"""Miscelaneous static pages"""

from flask import Blueprint, render_template, url_for, current_app
import re

static_pages = Blueprint('static_pages', __name__,
                         template_folder='templates',
                         static_folder='static',
                         # This should work without having to munge the static path,
                         # but the application's static path takes precedence
                         # if no url_prefix is specified:
                         # https://github.com/mitsuhiko/flask/issues/348
                         static_url_path='/static_pages/static')

@static_pages.route('/')
def landing_page():
    return render_template('index.html')

@static_pages.route('/api')
def api():
    return render_template(
        'api.html',
        endpoints=map(
            lambda rule: type('endpoint', (object,), dict(
                    rule=rule.rule,
                    methods=', '.join(set(rule.methods) - set(('HEAD', 'OPTIONS'))),
                    doc=current_app.view_functions[rule.endpoint].__doc__ or "")),
            sorted(filter(lambda rule: getattr(rule, 'defaults') and rule.defaults.get('ext') == 'json',
                          current_app.url_map.iter_rules()),
                   key=lambda rule: rule.endpoint)))
