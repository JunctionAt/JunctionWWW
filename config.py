import sqlalchemy
from blueprints import static_pages, beardstat, player_stats

# Create the DB connection
ENGINE = sqlalchemy.create_engine('mysql://junction:junction@localhost/junction')

# Blueprints to autoload. Each entry in the list gets passed as args to application.register_blueprint
BLUEPRINTS = [

    # Static pages
    {
        'blueprint': static_pages.static_pages
        },

    # PVE Player stats
    {
        'blueprint': player_stats.create_blueprint(
            'pve_player_stats',
            ENGINE,
            tablename='pve_stats',
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
            tablename='event_stats'),
        'url_prefix': '/player_stats/event'
        },
    ]
