__author__ = 'HansiHE'

from flask import render_template_string


badge_showcase_template = """
<div>
    {% for badge in badges %}
        <div>
            <img src="{{ badge['img_path'] }} title="{{ badge['description'] }}">
            <span>{{ badge['title'] }}</span>
        </div>
    {% endfor %}
</div>
"""


badges = dict()


def register_badge(badge_id, img_path, name, description):
    badges[badge_id] = dict(badge_id=badge_id, img_path=img_path, name=name, description=description)


def render_badges(user_profile, num=6):
    player_badges = list()
    for badge in user_profile.badges.values()[:num]:
        player_badges.append(badges[badge])
    return render_template_string(badge_showcase_template, badges=player_badges)