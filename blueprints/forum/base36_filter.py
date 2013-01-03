__author__ = 'HansiHE'

from flask import current_app
from jinja2 import evalcontextfilter
import base36

@current_app.template_filter()
@evalcontextfilter
def b36encode(eval_ctx, value):
    return base36.encode(value)

@current_app.template_filter()
@evalcontextfilter
def b36decode(eval_ctx, value):
    return base36.decode(value)