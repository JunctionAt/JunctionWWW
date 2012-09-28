from flask import current_app
from blueprints import auth, static_pages, avatar, player_notifications, player_stats, player_profiles, player_groups

# Markdown support
from flaskext.markdown import Markdown
Markdown(current_app)

# Blueprints to autoload. Each entry in the list gets passed as args to application.register_blueprint
BLUEPRINTS = [

    # Authentication
    dict(blueprint=auth.blueprint),
    
    # Static pages
    dict(blueprint=static_pages.static_pages),

    # Avatars
    dict(blueprint=avatar.avatar),
    
    # Player stats
    dict(blueprint=player_stats.player_stats([
                dict(name='pve', tablename='pve_stats',
                     hide=[
                        'comp.pk', 'kills.player', 'stats.lastlogout', 'stats.teleport', 'stats.chatletters', 'stats.chat'
                        ]),
                dict(name='event', tablename='event_stats',
                     hide=[
                        'stats.lastlogout', 'stats.teleport', 'stats.chatletters', 'stats.chat'
                        ]),
                ])),
    
    # Player profiles
    dict(blueprint=player_profiles.player_profiles),

    # Player grops (Clans & Cities)
    dict(blueprint=player_groups.player_groups([
                dict(name='pve',
                     group='city', groups='cities',
                     member='citizen', members='citizens',
                     owner='mayor', owners='mayors'),
                dict(name='survival',
                     group='clan', groups='clans',
                     owner='leader', owners='leaders'),
                ])),
    
    ]

