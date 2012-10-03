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
    debug = current_app.config.get('DEBUG', False)
    rules = sorted(current_app.url_map.iter_rules(), key=lambda rule: rule.endpoint) if debug else None
    return render_template('index.html', rules=rules, set=lambda *args: set(*args), list=lambda *args: list(*args))
