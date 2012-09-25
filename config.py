from blueprints import base, auth, static_pages, player_stats, player_profiles

PREFERRED_URL_SCHEME = 'https'

# Blueprints to autoload. Each entry in the list gets passed as args to application.register_blueprint
BLUEPRINTS = [

    # Comman declarative base and DB metadata binding
    {
        'blueprint': base.base,
        },
    
    # Authentication
    {
        'blueprint': auth.blueprint,
        },
    
    # Static pages
    {
        'blueprint': static_pages.static_pages
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
    
    # Player profiles
    {
        'blueprint': player_profiles.player_profiles
        },
    
    ]

