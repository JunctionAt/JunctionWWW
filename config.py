from blueprints import auth, static_pages, player_stats, player_profiles, player_groups

# Blueprints to autoload. Each entry in the list gets passed as args to application.register_blueprint
BLUEPRINTS = [

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
                ])
        },
    
    # Player profiles
    {
        'blueprint': player_profiles.player_profiles
        },

    # Clans & Cities
    {
        'blueprint': player_groups.player_groups([
                {
                    'name': 'pve',
                    'group': 'city',
                    'groups': 'cities',
                    'member': 'citizen',
                    'members': 'citizens',
                    'owner': 'mayor',
                    'owners': 'mayors'
                    },
                {
                    'name': 'survival',
                    'group': 'clan',
                    'groups': 'clans',
                    'owner': 'leader',
                    'owners': 'leaders'
                    },
                ])
        },
    
    ]

