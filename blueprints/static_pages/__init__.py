"""Miscelaneous static pages"""

from flask import Blueprint, Markup, render_template, url_for, current_app
from docutils.core import publish_parts
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

from blueprints.player_profiles import player_profiles
from blueprints.player_groups import player_groups
from blueprints.player_stats import player_stats
@static_pages.route('/api')
def api():
    return render_template(
        'api.html',
        blueprints=\
            map(lambda (blueprint, rules): (re.sub(r'^.*_', '', blueprint).capitalize(), to_html(globals().get(blueprint).__doc__ or ""), sorted(rules, key=lambda rule: (rule[1][0].endpoint, rule[0]))),
                reduce(lambda blueprints, rule: dict(blueprints.items() + [(rule[1][0].blueprint, blueprints.get(rule[1][0].blueprint, []) + [rule])]),
                       reduce(lambda rules, rule: dict(rules.items() + [(rule.rule, rules.get(rule.rule, []) + [rule])]),
                              map(lambda rule: type('endpoint', (object,),
                                                    dict(rule=rule.rule,
                                                         blueprint=rule.endpoint.split('.')[0],
                                                         endpoint=rule.endpoint,
                                                         methods=', '.join(set(rule.methods) - set(('HEAD', 'OPTIONS'))),
                                                         doc=to_html(current_app.view_functions[rule.endpoint].__doc__ or ""))),
                                  filter(lambda rule: (getattr(rule, 'defaults') or dict(ext='html')).get('ext') == 'json',
                                         current_app.url_map.iter_rules())),
                              dict()).iteritems(),
                       dict()).iteritems()
                ))

def to_html(docstring):
    return Markup(publish_parts(docstring,
                                writer_name='html',
                                settings_overrides={'doctitle_xform':False})['html_body'])
