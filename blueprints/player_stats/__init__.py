from flask import Blueprint, render_template, jsonify, abort
import sqlalchemy
import types
import re
from datetime import datetime

def player_stats(servers):
    """Generates a flask blueprint containing routes to all stat endpoints defined in servers"""

    blueprint = Blueprint('player_stats', __name__, template_folder='templates', static_folder='static')

    def create_route(name, engine=None, tablename='stats', table=None, session=None, show=[], hide=[], transforms=[], weights=[]):
        """Create a flask route that is an endpoint to a BeardStat db

        name -- required name of the new flask blueprint.
        engine -- sqlalchemy engine to query or current_app.config['ENGINE'].
        tablename -- name of table in engine to autoload from.
        table -- table class from sqlalchemy. One is created if None.
        session -- sqlalchemy query session loaded off this table. One is created if None.

        """
    
        # Define the route to get stats
        @blueprint.route('/%s/<player>.<ext>'%name)
        def stats(player, ext):

            # Lazy load the table structure
            _engine = engine
            if not _engine:
                from flask import current_app
                _engine = current_app.config['ENGINE']
                
            # Load the beardstat table if not provided one
            _table = table
            if not _table:
                from blueprints import beardstat
                _table = beardstat.load(_engine, tablename=tablename)

            # Create query session if not provided one
            _session = session
            if not session:
                from sqlalchemy.orm import create_session
                _session = create_session(_engine)

            stats = fetch_stats(_table, _session, player, show, hide, transforms, weights)
            if ext == 'json':
                return jsonify({ 'categories': stats })
            elif ext == 'html':
                return render_template('player_stats.html',
                                       name=name,
                                       categories=stats,
                                       player=player)

            # unsupported format requested
            abort(404)

    for server in servers:
        create_route(**server)

    return blueprint


"""Transform array (in order of precedence) for stat names and values

Each tuple contains a match str or lambda to capture and a str or lambda that renders.
If a lambda is used against a match, it can return a label string or a (label, value)

"""
__transforms__ = [
    
    # Proper category names
    ('blockdestroy.category', 'Blocks destroyed'),
    ('*.category', lambda cat: cat.category.capitalize()),

    # Some misc labels
    ('deaths.player', 'Deaths'),
    ('stats.armswing', 'Armswings'),
    ('stats.move', 'Meters walked'),
    ('stats.login', 'Number of logins'),
    ('stats.totalblockdestroy', 'Total blocks destroyed'),

    # Convert timestamps to strings
    ('stats.firstlogin', lambda stat: ('First login', datetime.fromtimestamp(stat.value).strftime('%Y-%m-%d'))),
    ('stats.lastlogin', lambda stat: ('Last login', datetime.fromtimestamp(stat.value).strftime('%Y-%m-%d'))),

    # Convert seconds to hour fractions
    ('stats.playedfor', lambda stat: ('Hours played', round(float(stat.value)/3600, 3))),
    
    # Proper block names
    ('blockdestroy.*', lambda stat: stat.stat.capitalize()),

    ]

"""Default hide array."""
__hide__ = [

    # Don't show block variation stats
    lambda stat: re.search('_\d+$', stat.stat),

    ]

"""Default sorting weight"""
__weights__ = [
    ('stats.category', 1),
    ('stats.playedfor', 1),
    ('stats.firstlogin', 2),
    ('stats.lastlogin', 3),
    ('stats.login', 4),
    ('stats.totalblockdestroy', 5),
    ]

def fetch_stats(table, session, player, show=[], hide=[], transforms=[], weights=[]):
    """Returns the proper stats for a given player name in table

    table -- table class from sqlalchemy.
    session -- sqlalchemy query session loaded off this table.
    hide -- list of stat names or lambdas to whitelist.
    show --  list of stat name or lambdas to blacklist.
    transforms -- list of tuples used to transform stat objects into readable information.
    weights -- list of tuples used to custom sort stat lists.
    
    """

    # Add suggested transforms and enforce a catch all
    transforms = transforms + __transforms__ + [('*.*', lambda stat: '%s.%s'%(stat.category,stat.stat))]
    hide = hide + __hide__
    
    # Add catch all to weights to sort by name
    weights = weights + __weights__ + [('*.*', lambda stat: '%s.%s'%(stat.category,stat.stat))]
    
    # Get the stats we want to show people
    visible = stat_visible(stat_rows(session, table, player), show, hide)

    return category_sorted(stat_sorted(stat_categorized(visible), weights, transforms), weights, transforms)

def category_sorted(categories, weights, transforms):
    """Return readable stat categories in a sorted list"""
    return map(lambda category: (lambda label: { 'name': label, 'stats': category['stats'] })
               (stat_transform(category_to_stat(category), transforms)),
               sorted(categories, key=stat_weight_key(weights, transform=category_to_stat)))

def stat_sorted(categories, weights, transforms):
    """Return a list of categories with sorted stats and readable names"""
    return [dict([('name', category), ('stats', map(
                        lambda stat: { 'name': stat[0][0], 'value': stat[0][1] },
                        sorted([(stat_transform(stat, transforms),stat) for stat in stats],
                               key=stat_weight_key(weights, transform=lambda stat: stat[1]))))])
            for category, stats in categories.iteritems()]

def stat_categorized(visible):
    """Return stats categorized in a dictionary"""
    return reduce(
        lambda categories, stat:
            dict(categories.items() + [(stat.category, categories.get(stat.category, []) + [stat])]),
        visible, {})

def stat_visible(rows, show, hide):
    """Filter stats by whitelist and blacklist rules"""
    return filter(
        lambda stat: (not len(show) or stat_match(stat, show)) and (not stat_match(stat, hide)),
        rows)

def stat_rows(session, table, player):
    """Return the raw stat rows from the db"""
    return session.query(table).filter(table.player==player).all()

def stat_transform(stat, transforms):
    """Transform a stat object into a readable tuple in form of (label, value)"""
    pattern = stat_match(stat, map(lambda transform: transform[0], transforms))
    transform = pair(pattern, transforms)[1]
    if isinstance(transform, types.FunctionType): transform = transform(stat)
    if stat.stat != 'category' and not isinstance(transform, types.TupleType):
        return (transform, stat.value)
    return transform

def stat_weight_key(weights, transform=None):
    """Return a key for sorting stats based on a custom weight table. transform will be applied to the stat if specified."""
    def key(stat):
        if transform:
            stat = transform(stat)
        pattern = stat_match(stat, map(lambda weight: weight[0], weights))
        weight = pair(pattern, weights)[1]
        if isinstance(weight, types.FunctionType):
            return weight(stat)
        return weight
    return key

def stat_match(stat, patterns):
    """Returns the string pattern or lambda from patterns that matches stat"""
    return reduce(
        lambda match, p:
            match or (p if (isinstance(p, types.FunctionType) and p(stat)) or
                      isinstance(p, types.StringType) and
                      (p[:p.index('.')] in [ '*', stat.category ] and
                       p[p.index('.')+1:] in [ '*', stat.stat ])
                      else False),
        patterns,
        False)

def category_to_stat(category):
    """Returns an object wrapping category's properties that can be used with stat functions"""
    return type('Stat', (object, ), {
            'category': category['name'],
            'stat': 'category',
            'value': category['stats'] })

def pair(first, tuples):
    """Returns the pair in tuples that has a specified first element"""
    return reduce(
        lambda match, pair: match or (pair if pair[0] == first else False),
        tuples,
        False)
