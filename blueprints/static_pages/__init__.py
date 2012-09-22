from flask import Blueprint, render_template, url_for

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
