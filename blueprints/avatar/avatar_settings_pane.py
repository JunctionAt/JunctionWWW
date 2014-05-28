from blueprints.settings.views import add_settings_pane
from flask import url_for


add_settings_pane(lambda: url_for('avatar.avatar_control'), "Account", "Profile Picture", menu_id="avatar")
