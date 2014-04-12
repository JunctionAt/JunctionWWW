from werkzeug.local import LocalProxy
from . import extension_access

# Mostly for backwards compatibility
cache = LocalProxy(lambda: getattr(extension_access, "cache", None))
mongo = LocalProxy(lambda: getattr(extension_access, "mongo", None))
mail = LocalProxy(lambda: getattr(extension_access, "mail", None))
admin = LocalProxy(lambda: getattr(extension_access, "admin", None))
rest_api = LocalProxy(lambda: getattr(extension_access, "rest_api", None))
markdown = LocalProxy(lambda: getattr(extension_access, "markdown", None))