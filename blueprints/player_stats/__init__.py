"""
Player Stats
------------

Realtime player stats.
"""

import flask
from flask import render_template, jsonify, abort, current_app
from datetime import datetime
import types

from blueprints.base import Base, session, db
from blueprints.api import apidoc


class Blueprint(flask.Blueprint):

    endpoints = dict()

    def __call__(self, servers=[]):
        for server in servers:
            self[server['name']] = Endpoint(**server)
        return self

    def __getitem__(self, server):
        return self.endpoints[server]

    def __setitem__(self, server, endpoint):
        self.endpoints[server] = endpoint

player_stats = Blueprint('player_stats', __name__, template_folder='templates')

class Endpoint(object):
    """Wrapper for calls to PlayerStats that contain db or table specifics"""

    def __init__(self, name, tablename='stats', show=[], hide=[], transforms=[], weights=[]):
        """Create a BeardStat endpoint

        name -- required name of the new flask blueprint.
        tablename -- name of table in engine to autoload from.

        """

        self.model = type(tablename, (Base,), dict(
                __tablename__=tablename,
                player=db.Column(db.String(32), primary_key=True),
                category=db.Column(db.String(32), primary_key=True),
                stat=db.Column(db.String(32), primary_key=True),
                value=db.Column(db.Integer)))
        
        self.name = name
        self.tablename = tablename
        self.show = show
        self.hide = hide
        self.transforms = transforms
        self.weights = weights
        
        player_stats.add_url_rule('/%s/stats/<player>'%self.name, 'show_stats', defaults=dict(server=self.name, ext='html'))
        
    def get_by_name(self, player):
        return PlayerStats.player_stats(self.model, player, self.show, self.hide, self.transforms, self.weights)
    
    def format(self, rows):
        return PlayerStats.stat_format(rows, self.show, self.hide, self.transforms, self.weights)


@apidoc(__name__, player_stats, '/<server>/stats/<player>.json', endpoint='show_stats', defaults=dict(ext='json'))
def show_stats_api(server, player, ext):
    """
    Returns a weighted list of stat categories for ``player``. Eg.:

    .. code-block::
    
       {
           "wiggitywhack": [
               {
                   "name": "Stats",
                   "stats": [
                       {
                           "name": "Hours played",
                           "value": 0.783
                       },
                       {
                           "name": "First login",
                           "value": "2012-09-22"
                       },
                       {
                           "name": "Meters walked",
                           "value": 21
                       }
                   ]
               },
               {
                   "name": "Deaths",
                   "stats": [
                       {
                           "name": "Deaths",
                           "value": 0
                       }
                   ]
               },
           ]
       }
    """

@player_stats.route('/<server>/stats/<player>', defaults=dict(ext='html'))
def show_stats(server, player, ext):
    try:
        endpoint = player_stats[server]
    except KeyError:
        abort(404)
    stats = endpoint.get_by_name(player)
    if not len(stats):
        abort(404)
    if ext == 'json':
        return jsonify({player:stats})
    elif ext == 'html':
        return render_template('player_stats.html', categories=stats)

"""Transform array (in order of precedence) for stat names and values

Each tuple contains a match str or lambda to capture and a str or lambda that renders.
If a lambda is used against a match, it can return a label string or a (label, value).

These transforms are appended to any supplied list of transforms passed to fetch_stats.

"""
__transforms__ = [
    
    # Proper category names
    ('blockdestroy.category', 'Blocks destroyed'),
    ('blockcreate.category', 'Blocks placed'),
    ('damagedealt.category', 'Damage dealt'),
    ('damagetaken.category', 'Damage taken'),
    ('*.category', lambda cat: cat.category.capitalize()),

    # Some misc labels
    ('deaths.player', 'Deaths'),
    ('stats.damagehealed', 'Total healed'),
    ('stats.healsatiated', 'Healed from food'),
    ('stats.magicregen', 'Healed from magic'),
    ('stats.armswing', 'Armswings'),
    ('stats.move', 'Meters walked'),
    ('stats.login', 'Number of logins'),
    ('stats.totalblockdestroy', 'Total blocks destroyed'),
    ('stats.totalblockcreate', 'Total blocks placed'),

    # Convert timestamps to strings
    ('stats.firstlogin', lambda stat:
         ('First login', datetime.fromtimestamp(stat.value).strftime('%Y-%m-%d'))),
    ('stats.lastlogin', lambda stat:
         ('Last login', datetime.fromtimestamp(stat.value).strftime('%Y-%m-%d'))),

    # Convert seconds to hour fractions
    ('stats.playedfor', lambda stat:
         ('Hours played', round(float(stat.value)/3600, 3))),
    
    # Proper block names
    ('blockdestroy.*', lambda stat:
         stat.stat.capitalize()),
    ('blockcreate.*', lambda stat:
         stat.stat.capitalize()),

    # Proper mob names
    ('kills.*', lambda stat:
         stat.stat.capitalize()),
    ('damagetaken.*', lambda stat:
         stat.stat.capitalize()),
    ('damagedealt.entityattack', 'Total attack'),
    ('damagedealt.*', lambda stat:
         stat.stat.capitalize()),

    ]

"""Default hide array."""
__hide__ = [

    # Don't show block variation stats
    # this might break. if you're the one who is fixing it, please don't use regex
    lambda stat: stat.stat[-2] == '_' and stat.stat[-1] in '0123456789',

    ]

"""Default sorting weight"""
__weights__ = [
    ('stats.category',),
    ('stats.playedfor',),
    ('stats.firstlogin',),
    ('stats.lastlogin',),
    ('stats.login',),
    ('stats.totalblockdestroy',),
    ('stats.totalblockcreate',),
    ]


class PlayerStats:
    """Container for the data crunching methods"""

    @staticmethod
    def player_stats(model, player, show=[], hide=[], transforms=[], weights=[]):
        """Returns the proper stats for a given player name in table

        model -- model class from sqlalchemy.
        hide -- list of stat names or lambdas to whitelist.
        show --  list of stat name or lambdas to blacklist.
        transforms -- list of tuples used to transform stat objects into readable information.
        weights -- list of tuples used to custom sort stat lists.
        
        """
        
        return PlayerStats.stat_format(session.query(model).filter(model.player==player).all(),
                                       show, hide, transforms, weights)

    @staticmethod
    def stat_format(rows, show=[], hide=[], transforms=[], weights=[]):
        
        # Add suggested transforms and enforce a catch all
        transforms = transforms + __transforms__ + [('*.*', lambda stat: '%s.%s'%(stat.category,stat.stat))]
        hide = hide + __hide__
        
        # Add catch all to weights to sort by name
        weights = weights + __weights__ + [('*.*', lambda stat: '%s.%s'%(stat.category,stat.stat))]
        
        # Get the stats we want to show people
        filtered = PlayerStats.stat_filter(rows, show, hide)

        return \
            PlayerStats.category_sorted(
            PlayerStats.stat_sorted(
                    PlayerStats.stat_categorized(filtered),
                    weights, transforms),
            weights, transforms)        

    @staticmethod
    def category_sorted(categories, weights, transforms):
        """Return readable stat categories in a sorted list"""
        return map(lambda category: (lambda label: dict(name=label, stats=category['stats']))
                   (PlayerStats.stat_transform(PlayerStats.category_to_stat(category), transforms)),
                   sorted(categories, key=PlayerStats.stat_weight_key(weights, transform=PlayerStats.category_to_stat)))

    @staticmethod
    def stat_sorted(categories, weights, transforms):
        """Return a list of categories with sorted stats and readable names"""
        return [dict([('name', category), ('stats', map(
                            lambda stat: dict(name=stat[0][0], value=stat[0][1]),
                            sorted([(PlayerStats.stat_transform(stat, transforms),stat) for stat in stats],
                                   key=PlayerStats.stat_weight_key(weights, transform=lambda stat: stat[1]))))])
                for category, stats in categories.iteritems()]

    @staticmethod
    def stat_categorized(visible):
        """Return stats categorized in a dictionary"""
        return reduce(
            lambda categories, stat:
                dict(categories.items() + [(stat.category, categories.get(stat.category, []) + [stat])]),
            visible, dict())

    @staticmethod
    def stat_filter(rows, show, hide):
        """Filter stats by whitelist and blacklist rules"""
        return filter(
            lambda stat:
                (not len(show) or PlayerStats.stat_match(stat, show)) and \
                (not PlayerStats.stat_match(stat, hide)),
            rows)

    @staticmethod
    def stat_transform(stat, transforms):
        """Transform a stat object into a readable tuple in form of (label, value)"""
        pattern = PlayerStats.stat_match(stat, map(lambda transform: transform[0], transforms))
        transform = PlayerStats.pair(pattern, transforms)[1]
        if callable(transform): transform = transform(stat)
        if stat.stat != 'category' and not isinstance(transform, types.TupleType):
            return (transform, stat.value)
        return transform

    @staticmethod
    def stat_weight_key(weights, transform=None):
        """Return a key for sorting stats based on a custom weight table. transform will be applied to the stat if specified."""
        def key(stat):
            if transform:
                stat = transform(stat)
            pattern = PlayerStats.stat_match(stat, map(lambda weight: weight[0], weights))
            pair = PlayerStats.pair(pattern, weights)
            return weights.index(pair) if len(pair) == 1 else pair[1](stat) if callable(pair[1]) else pair[1]
        return key

    @staticmethod
    def stat_match(stat, patterns):
        """Returns the string pattern or lambda from patterns that matches stat"""
        return reduce(
            lambda match, p:
                match or (p if (callable(p) and p(stat)) or
                          isinstance(p, types.StringType) and
                          (p[:p.index('.')] in [ '*', stat.category ] and
                           p[p.index('.')+1:] in [ '*', stat.stat ])
                          else False),
            patterns,
            False)

    @staticmethod
    def category_to_stat(category):
        """Returns an object wrapping category's properties that can be used with stat functions"""
        return type('Stat', (object, ), dict(
                category=category['name'],
                stat='category',
                value=category['stats']))

    @staticmethod
    def pair(first, tuples):
        """Returns the pair in tuples that has a specified first element"""
        return reduce(
            lambda match, pair: match or (pair if pair[0] == first else False),
            tuples,
            False)
