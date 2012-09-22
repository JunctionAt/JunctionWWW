import sqlalchemy
from blueprints import beardstat, player_stats

# Create the DB connection
ENGINE = sqlalchemy.create_engine('mysql://junction:junction@localhost/junction')

# Blueprint to autoload. Each entry in the list gets passed as args to application.register_blueprint
BLUEPRINTS = [

    # PVE Player stats
    {
        'blueprint': player_stats.create_blueprint(
            'pve_player_stats',
            ENGINE,
            beardstat.load(ENGINE, table='pve_stats'),
            hide=[
                'comp.pk', 'kills.player', 'stats.lastlogout', 'stats.teleport', 'stats.chatletters', 'stats.chat'
                ]),
        'url_prefix': '/player_stats/pve'
        },

    # Event Player stats
    {
        'blueprint': player_stats.create_blueprint(
            'event_player_stats',
            ENGINE,
            beardstat.load(ENGINE, table='event_stats')),
        'url_prefix': '/player_stats/event'
        },
    ]
