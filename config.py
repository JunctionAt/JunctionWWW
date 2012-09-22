from blueprints import static_pages, auth, player_stats, player_profiles
from blueprints import static_pages, player_stats

# Blueprints to autoload. Each entry in the list gets passed as args to application.register_blueprint
BLUEPRINTS = [

    # Static pages
    {
        'blueprint': static_pages.static_pages
        },

    # Authentication
    {
        'blueprint': auth.blueprint,
        },
    # Player profiles
    {
        'blueprint': player_profiles.player_profiles
        },
    
    # Player stats
    {
        'blueprint': player_stats.player_stats([
                {
                    'name': 'pve', 'tablename': 'pve_stats', 'hide': [
                        'comp.pk', 'kills.player', 'stats.lastlogout', 'stats.teleport', 'stats.chatletters', 'stats.chat'
                        ]},
                {
                    'name': 'event', 'tablename': 'event_stats', 'hide': [
                        'stats.lastlogout', 'stats.teleport', 'stats.chatletters', 'stats.chat'
                        ]},
                ]),
        'url_prefix': '/stats'
        },
    ]

