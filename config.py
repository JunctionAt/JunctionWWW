import flask
from blueprints import auth, static_pages, avatar, player_notifications, player_stats, player_profiles, player_groups

# Blueprints to autoload. Each entry in the list gets passed as args to application.register_blueprint
BLUEPRINTS = [

    # Authentication
    dict(blueprint=auth.blueprint),
    
    # Static pages
    dict(blueprint=static_pages.static_pages),

    # Notifications
    dict(blueprint=player_notifications.player_notifications),

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

    # Player groups (Clans & Cities)
    dict(blueprint=player_groups.player_groups([
                dict(name='pve', group='city', groups='cities', member='citizen', owner='mayor'),
                dict(name='survival', group='clan', owner='leader'),
                ])),
    
    ]


# Markdown support
from flaskext.markdown import Markdown
Markdown(flask.current_app)

# Server name global
@flask.current_app.context_processor
def inject_server():
    return dict(server_display_name=lambda server: dict(pve='PvE', survival='Survival', event='Event')[server],)

