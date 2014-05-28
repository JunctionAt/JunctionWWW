from flask import current_app
from werkzeug.local import LocalProxy

extension_access = LocalProxy(lambda: getattr(current_app, "extension_access_object", None))
