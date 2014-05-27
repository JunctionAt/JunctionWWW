__author__ = 'HansiHE'

from flask import render_template_string
from config.badges import BADGES


badge_showcase_template = """
<div>
    {% for badge in badges %}
        <div>
            <img src="{{ badge['img_path'] }}" class="player-badge" title="{{ badge['description'] }}">
            <span>{{ badge['name'] }}</span>
        </div>
    {% endfor %}
</div>
"""

badges = {}


def register_badge(m):
    badges[m['badge_id']] = dict(m)


def render_badges(user_profile, num=6):
    player_badges = []
    for badge in list(sorted(user_profile.badges, key=lambda b: badges[b]['priority'], reverse=True))[:num]:
        player_badges.append(badges[badge])
    return render_template_string(badge_showcase_template, badges=player_badges)

for b in BADGES:
    register_badge(b)
