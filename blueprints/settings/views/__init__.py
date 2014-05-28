settings_panels_structure = dict()


def add_settings_pane(url, category, name, menu_id=None):
    if category not in settings_panels_structure:
        settings_panels_structure[category] = dict()

    settings_panels_structure[category][name] = dict(
        url=url,
        menu_id=menu_id if menu_id is not None else name)