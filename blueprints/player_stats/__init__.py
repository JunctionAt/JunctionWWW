from flask import Blueprint, render_template, jsonify, abort, current_app
import sqlalchemy
from sqlalchemy.orm import create_session
import types
import re
from datetime import datetime

def player_stats(servers):
    """Create routes for all stat endpoints defined in servers

    Use player_stats.endpoints['server_name'] to get the autoloaded table (e.table)
    or call player_stats form these endpoints.

    Returns the blueprint for easy setup.
    
    """

    for server in servers:
        endpoints[server['name']] = Endpoint(**server)

    return blueprint
    

# Endpoints
endpoints = dict()

# The Flask blueprint
blueprint = Blueprint('player_stats', __name__,
                      template_folder='templates',
                      static_folder='static')

class Endpoint(object):
    """Wrapper for calls to PlayerStats that contain db or table specifics"""

    def __init__(self, name, engine=None, tablename='stats', table=None,
                 show=[], hide=[], transforms=[], weights=[]):

        """Create a BeardStat endpoint

        name -- required name of the new flask blueprint.
        engine -- sqlalchemy engine to query or current_app.config['ENGINE'].
        tablename -- name of table in engine to autoload from.
        table -- table class from sqlalchemy. One is created if None.
        session -- sqlalchemy query session loaded off this table. One is created if None.

        """

        self._engine = None
        self._table = None
        self._session = None
        self.name = name
        self.engine = engine
        self.tablename = tablename
        self.table = table
        self.show = show
        self.hide = hide
        self.transforms = transforms
        self.weights = weights
        self.session = None
        
        # Define a route to get stats
        @blueprint.route('/%s/<player>.<ext>'%name)
        def stats(player, ext):
            stats = self.player_stats(player)
            if ext == 'json':
                return jsonify({ 'categories': stats })
            elif ext == 'html':
                return render_template('player_stats.html',
                                       name=name,
                                       categories=stats,
                                       player=player)

            # unsupported format requested
            abort(404)
    
    def player_stats(self, player):
        return PlayerStats.player_stats(self.table, self.session, player,
                                        self.show, self.hide, self.transforms, self.weights)

    def get_engine(self):
        if not self._engine:
            self._engine = current_app.config['ENGINE']
        return self._engine
        
    def set_engine(self, engine):
        self._engine = engine

    def get_table(self):
        if not self._table:
            from blueprints import beardstat
            self._table = beardstat.load(self.engine, self.tablename)
        return self._table
        
    def set_table(self, table):
        self._table = table

    def get_session(self):
        if not self._session:
            self._session = create_session(self.engine)
        return self._session
        
    def set_session(self, session):
        self._session = session

    engine = property(fget=get_engine, fset=set_engine)
    table = property(fget=get_table, fset=set_table)
    session = property(fget=get_session, fset=set_session)


"""Transform array (in order of precedence) for stat names and values

Each tuple contains a match str or lambda to capture and a str or lambda that renders.
If a lambda is used against a match, it can return a label string or a (label, value).

These transforms are appended to any supplied list of transforms passed to fetch_stats.

"""
__transforms__ = [
    
    # Proper category names
    ('blockdestroy.category', 'Blocks destroyed'),
    ('*.category', lambda cat:
         cat.category.capitalize()),

    # Some misc labels
    ('deaths.player', 'Deaths'),
    ('stats.armswing', 'Armswings'),
    ('stats.move', 'Meters walked'),
    ('stats.login', 'Number of logins'),
    ('stats.totalblockdestroy', 'Total blocks destroyed'),

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


class PlayerStats:
    """Container for the data crunching methods"""

    @staticmethod
    def player_stats(table, session, player, show=[], hide=[], transforms=[], weights=[]):
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
        filtered = PlayerStats.stat_filter(
            PlayerStats.stat_rows(session, table, player),
            show, hide)

        return \
            PlayerStats.category_sorted(
            PlayerStats.stat_sorted(
                    PlayerStats.stat_categorized(filtered),
                    weights, transforms),
            weights, transforms)

    @staticmethod
    def category_sorted(categories, weights, transforms):
        """Return readable stat categories in a sorted list"""
        return map(lambda category: (lambda label: { 'name': label, 'stats': category['stats'] })
                   (PlayerStats.stat_transform(PlayerStats.category_to_stat(category), transforms)),
                   sorted(categories, key=PlayerStats.stat_weight_key(weights, transform=PlayerStats.category_to_stat)))

    @staticmethod
    def stat_sorted(categories, weights, transforms):
        """Return a list of categories with sorted stats and readable names"""
        return [dict([('name', category), ('stats', map(
                            lambda stat: { 'name': stat[0][0], 'value': stat[0][1] },
                            sorted([(PlayerStats.stat_transform(stat, transforms),stat) for stat in stats],
                                   key=PlayerStats.stat_weight_key(weights, transform=lambda stat: stat[1]))))])
                for category, stats in categories.iteritems()]

    @staticmethod
    def stat_categorized(visible):
        """Return stats categorized in a dictionary"""
        return reduce(
            lambda categories, stat:
                dict(categories.items() + [(stat.category, categories.get(stat.category, []) + [stat])]),
            visible, {})

    @staticmethod
    def stat_filter(rows, show, hide):
        """Filter stats by whitelist and blacklist rules"""
        return filter(
            lambda stat:
                (not len(show) or PlayerStats.stat_match(stat, show)) and \
                (not PlayerStats.stat_match(stat, hide)),
            rows)

    @staticmethod
    def stat_rows(session, table, player):
        """Return the raw stat rows from the db"""
        return session.query(table).filter(table.player==player).all()

    @staticmethod
    def stat_transform(stat, transforms):
        """Transform a stat object into a readable tuple in form of (label, value)"""
        pattern = PlayerStats.stat_match(stat, map(lambda transform: transform[0], transforms))
        transform = PlayerStats.pair(pattern, transforms)[1]
        if isinstance(transform, types.FunctionType): transform = transform(stat)
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
            weight = PlayerStats.pair(pattern, weights)[1]
            if isinstance(weight, types.FunctionType):
                return weight(stat)
            return weight
        return key

    @staticmethod
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

    @staticmethod
    def category_to_stat(category):
        """Returns an object wrapping category's properties that can be used with stat functions"""
        return type('Stat', (object, ), {
                'category': category['name'],
                'stat': 'category',
                'value': category['stats'] })

    @staticmethod
    def pair(first, tuples):
        """Returns the pair in tuples that has a specified first element"""
        return reduce(
            lambda match, pair: match or (pair if pair[0] == first else False),
            tuples,
            False)