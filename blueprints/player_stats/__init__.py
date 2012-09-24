from flask import Blueprint, render_template, jsonify, abort, current_app
import sqlalchemy
import sqlalchemy.orm
import types
import re
from datetime import datetime
from blueprints.beardstat import beardstat

def player_stats(servers=[]):
    """Create routes for all stat endpoints defined in servers
    
    Use player_stats.endpoints['server_name'] to get the autoloaded model (endpoints['pve_stats'].model)
    or call player_stats from these endpoints.
    
    Returns the blueprint for easy setup.
    
    """
    
    for server in servers:
        player_stats.endpoints[server['name']] = Endpoint(**server)

    return player_stats.blueprint


# Endpoints
endpoints = dict()
player_stats.endpoints = endpoints

# Blueprint
blueprint = Blueprint('player_stats', __name__, template_folder='templates')
player_stats.blueprint = blueprint

class Endpoint(object):
    """Wrapper for calls to PlayerStats that contain db or table specifics"""

    def __init__(self, name, engine=None, tablename='stats',
                 show=[], hide=[], transforms=[], weights=[]):
        """Create a BeardStat endpoint

        name -- required name of the new flask blueprint.
        engine -- sqlalchemy engine to query or current_app.config['ENGINE'].
        tablename -- name of table in engine to autoload from.
        model -- model class from sqlalchemy. One is created if None.
        session -- sqlalchemy query session loaded off this table. One is created if None.

        """

        self.model = beardstat(tablename)
        self._engine = engine
        self._session = None
        self.name = name
        self.tablename = tablename
        self.show = show
        self.hide = hide
        self.transforms = transforms
        self.weights = weights
        self.session = None
        
        # Define a route to get stats
        def player_stats(player, ext):
            stats = self.get_by_name(player)
            if ext == 'json':
                return jsonify({ 'categories': stats })
            elif ext == 'html':
                return render_template('player_stats.html', categories=stats)

            # unsupported format requested
            abort(404)
        
        blueprint.add_url_rule('/%s/<player>.<ext>'%name, name, player_stats)
    
    def get_by_name(self, player):
        return PlayerStats.player_stats(self.model, self.session, player,
                                        self.show, self.hide, self.transforms, self.weights)
    
    def format(self, rows):
        return PlayerStats.stat_format(rows, self.show, self.hide, self.transforms, self.weights)

    @property
    def engine(self):
        if not self._engine:
            self._engine = current_app.config['ENGINE']
        return self._engine

    @engine.setter
    def engine(self, engine):
        self._engine = engine

    @property
    def session(self):
        if not self._session:
            self._session = sqlalchemy.orm.sessionmaker(self.engine)()
        return self._session

    @session.setter
    def session(self, session):
        self._session = session


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
    def player_stats(model, session, player, show=[], hide=[], transforms=[], weights=[]):
        """Returns the proper stats for a given player name in table

        model -- model class from sqlalchemy.
        session -- sqlalchemy query session loaded off this table.
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
