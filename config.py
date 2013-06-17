import flask
from blueprints import (auth, notifications, static_pages, api, avatar,
                        logs, bans, forum, wiki, player_groups, admin,
                        player_profiles, donations, staff, settings)

# Blueprints to autoload. Each entry in the list gets passed as args to application.register_blueprint
BLUEPRINTS = [

    # Authentication
    dict(blueprint=auth.blueprint),

    # Notifications
    dict(blueprint=notifications.blueprint),
    
    # Static pages
    dict(blueprint=static_pages.static_pages),

    # API Doc
    dict(blueprint=api.api),

    # Logs
    dict(blueprint=logs.logs),

    # Avatars
    dict(blueprint=avatar.avatar),
    
    # Player stats
    #dict(blueprint=player_stats.player_stats([
    #            dict(name='pve', tablename='pve_stats',
    #                 hide=[
    #                    'comp.pk', 'kills.player', 'stats.lastlogout', 'stats.teleport', 'stats.chatletters', 'stats.chat'
    #                    ]),
    #            dict(name='event', tablename='event_stats',
    #                 hide=[
    #                    'stats.lastlogout', 'stats.teleport', 'stats.chatletters', 'stats.chat'
    #                    ]),
    #            dict(name='chaos', tablename='chaos_stats',
    #                 hide=[
    #                    'stats.lastlogout', 'stats.teleport', 'stats.chatletters', 'stats.chat'
    #                    ]),
   #             ])),
    
    # Player profiles
    dict(blueprint=player_profiles.blueprint),

    # Player groups (Clans & Cities)
    #dict(blueprint=player_groups.player_groups([
    #            dict(name='pve', group='city', groups='cities', member='citizen', owner='mayor'),
    #            dict(name='survival', group='clan', owner='leader'),
    #            ])),

    # Bans
    dict(blueprint=bans.bans),
    
    # Forum
    dict(blueprint=forum.blueprint),

    #Wiki
    dict(blueprint=wiki.blueprint),

    #Administration stuffs
    #dict(blueprint=admin.blueprint),

    dict(blueprint=donations.blueprint),

    dict(blueprint=staff.blueprint),

    dict(blueprint=settings.blueprint)

    ]


# Markdown support
from flaskext.markdown import Markdown
Markdown(flask.current_app)

# Server name global
@flask.current_app.context_processor
def inject_server():
    return dict(server_display_name=lambda server: dict(pve='PvE', survival='Survival', event='Event', chaos='Chaos', staff='Staff')[server],)

UPLOAD_FOLDER = "/tmp/www/uploads"

# Recaptcha
RECAPTCHA_USE_SSL = True
RECAPTCHA_PUBLIC_KEY = '6LdkRtkSAAAAAMtMsr3JLyMcNN-2dsMSpeLM5CvB'
RECAPTCHA_PRIVATE_KEY = '6LdkRtkSAAAAAA8EBjvIX38Z62LIpNmAbFNseNqh'