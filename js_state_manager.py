from flask import g, current_app
import json


class JsStateManager(dict):
    def render(self):
        return json.dumps(self)


def get_manager():
    """
    Returns the js state manager for the current request.
    """
    manager = getattr(g, 'js_state_manager', None)
    if manager is None:
        manager = JsStateManager()
        g.js_state_manager = manager
    return manager


request_state_injectors = list()


def inject_js_state(func):
    """
    Functions decorated with this decorator will be called on each request, and their returned dictionary will be
    merged with the js state dictionary.
    """
    request_state_injectors.append(func)
    return func


@current_app.context_processor
def js_state_context_processor():
    for injector in request_state_injectors:
        get_manager().update(injector())

    return dict(
        js_state = get_manager()
    )