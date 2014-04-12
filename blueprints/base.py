from werkzeug.local import LocalProxy
from . import extension_access


def extension_access_proxy(name):
    return LocalProxy(lambda: getattr(extension_access, name, None))

# Mostly for backwards compatibility
cache = extension_access_proxy("cache")
mongo = extension_access_proxy("mongo")
mail = extension_access_proxy("mail")
admin = extension_access_proxy("admin")
rest_api = extension_access_proxy("rest_api")
markdown = extension_access_proxy("markdown")
assets = extension_access_proxy("assets")