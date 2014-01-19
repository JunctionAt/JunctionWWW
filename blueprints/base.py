from flask import current_app
from flask.ext.cache import Cache
from mongoengine import connect
from flask_superadmin import Admin
from flask.ext.mail import Mail
from flask_wtf import CsrfProtect
from flask.ext.markdown import Markdown
from api_hack import RestfulApiCsrf


cache = Cache(current_app, config={'CACHE_TYPE': 'simple'})

mongo = connect("pf")

mail = Mail(current_app)

csrf = CsrfProtect(current_app)

rest_api = RestfulApiCsrf(current_app, prefix="/api", csrf=csrf)

markdown = Markdown(current_app, safe_mode="escape")

import blueprints.admin
