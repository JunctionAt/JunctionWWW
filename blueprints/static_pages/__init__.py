from flask import Blueprint, current_app, render_template, url_for, redirect
from flask import send_file

static_pages = Blueprint('static_pages', __name__, template_folder='templates')


@current_app.errorhandler(404)
def error_404(e):
    return render_template('404.html'), 404


@current_app.errorhandler(403)
def error_403(e):
    return render_template('403.html'), 403


# For April Fools - uncomment this, comment / on landing_page
# @static_pages.route('/')
# def woohoo():
#     return redirect(url_for('static_pages.landing_page'))

# @static_pages.route('/cgi-bin/main.pl')
@static_pages.route('/')
def landing_page():
    return render_template('index.html', title="Home")


@static_pages.route('/servers/')
def view_servers():
    return render_template('servers.html', title="Servers")


@static_pages.route('/appeal')
def appeal_redir():
    return redirect(url_for('wiki.display_wiki_article', wiki_url="appeal"))


@static_pages.route('/favicon.ico')
def favicon():
    return send_file('static/favicon.ico')
