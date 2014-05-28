__author__ = 'HansiHE'

from blueprints import (auth, notifications, static_pages, api, avatar,
                        bans, forum, wiki, modreq, alts, player_profiles,
                        groups, donations, staff, settings, calendar, servers, admin)

# Blueprints to autoload.
# Each entry in the list gets passed as args to application.register_blueprint
BLUEPRINTS = [

    # Authentication
    dict(blueprint=auth.blueprint),

    # Notifications
    dict(blueprint=notifications.blueprint),

    # Static pages
    dict(blueprint=static_pages.static_pages),

    # API
    dict(blueprint=api.blueprint),

    # Avatars
    dict(blueprint=avatar.avatar),

    # Player stats
    # dict(blueprint=player_stats.player_stats([
    #     dict(name='pve', tablename='pve_stats',
    #          hide=['comp.pk', 'kills.player', 'stats.lastlogout', 'stats.teleport', 'stats.chatletters', 'stats.chat']),
    #     dict(name='event', tablename='event_stats',
    #          hide=['stats.lastlogout', 'stats.teleport', 'stats.chatletters', 'stats.chat']),
    #     dict(name='chaos', tablename='chaos_stats',
    #          hide=['stats.lastlogout', 'stats.teleport', 'stats.chatletters', 'stats.chat']),
    # ])),

    # Player profiles
    dict(blueprint=player_profiles.blueprint),

    # Player groups (Clans & Cities)
    dict(blueprint=groups.get_blueprint()),
    # dict(blueprint=player_groups.player_groups([
    #     dict(name='pve', group='city', groups='cities', member='citizen', owner='mayor'),
    #     dict(name='survival', group='clan', owner='leader'),
    # ])),

    # Bans
    dict(blueprint=bans.bans),

    # Alts
    dict(blueprint=alts.alts),

    # Forum
    dict(blueprint=forum.blueprint),

    # Wiki
    dict(blueprint=wiki.blueprint),

    # Administration stuffs
    # dict(blueprint=admin.blueprint),

    # Donations
    dict(blueprint=donations.blueprint),

    # Our Amazing Staff
    dict(blueprint=staff.blueprint),

    # Calendar
    # dict(blueprint=calendar.blueprint),

    # Account Settings
    dict(blueprint=settings.blueprint)]
