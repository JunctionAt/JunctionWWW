"""
Introduction
============

This document describes the API to the Junction site and Minecraft servers. It is an HTTP and JSON service
that can be used to access any of the information on the web front-end.

All URIs and arguments are case-sensitive. The server will redirect to the preferred capitalization of these
resources with a 301 status code.

Data provided by the user in a request body must be either form or JSON encoded.
`JSON data must be sent with a` ``Content-Type: application/json`` `request header`.

----

Response Codes
==============

The server will use status codes as abbreviated responses and consolidate data sent by redirecting to relevant
endpoints upon success.  It is often adequate to act upon a response by its status code alone, without following its
redirect or parsing the response body. The following section contains an explaination on how status codes are
used by the API.

200
  Resource found. The response body will be JSON data.
301
  Resource can be found at preferred URI. Do not use the requested URI in the future. Send the same request to provided URI to complete operation.
302
  Resource found or assertion succeeded. Follow redirect with a GET request for relevant JSON data.
303
  Operation successful. You may follow the redirect with a GET request, but is not guaranteed to return a successful status code depending on the operation performed.
307
  Temporary redirect. Send the same request to provided URI to complete operation. *Note:* The same request may be available at this URI in the future.
400
  Operation unsuccessfull. Relevant JSON data may be provided in the response body.
403
  Your account does not have permission to perform the requested operation.
404
  Resource not found or assertion failed.
500
  Internal Error. Does not indicate an invalid request. You may try the same request later for successful completion.

The following sections describe the available endpoints and their accepted methods.
"""

from flask import Blueprint, Markup, render_template, current_app
from docutils.core import publish_parts
from werkzeug.utils import import_string
import re

__order__ = []
__endpoints__= dict()

class apidoc(object):
    """Mark a view function as being documented on the API page."""

    def __init__(self, import_name, blueprint, rule, **kwargs):
        self.import_name = import_name
        self.module_name = import_name.split('.')[-1]
        self.blueprint = blueprint
        self.rule = rule
        self.method = kwargs.get('methods', ('GET',))[0]
        self.endpoint = kwargs.pop('endpoint', None)
        self.kwargs = kwargs

    def __call__(self, func):
        global __order__, __endpoints__
        route = False
        if not self.endpoint:
            route = True
            self.endpoint = func.__name__
        self.doc = to_html(func.__doc__)
        __order__ += [self]
        endpoints = __endpoints__.get(self.import_name, dict())
        __endpoints__[self.import_name] = endpoints
        if not self.import_name in __order__: __order__ += [self.import_name]
        rule = re.sub('<p>|</p>', '', to_html(re.sub(r'(<[^>]+>)', '``\\1``', self.rule))).strip()
        methods = endpoints.get(rule, list())
        endpoints[rule] = methods
        if not rule in __order__: __order__ += [rule]
        methods += [self]
        if route:
            return self.blueprint.route(self.rule, **self.kwargs)(func)
        return self.blueprint.add_url_rule(self.rule, self.endpoint, **self.kwargs)

api = Blueprint('api', __name__, template_folder='templates')

@api.route('/api')
def apidocs():
    return render_template(
        'api.html',
        doc=to_html(__doc__, indent=None),
        blueprints=\
            map(lambda pair:
                    (reduce(lambda first, line: first or line, (import_string(pair[0]).__doc__ or "").split('\n'), ""),
                     to_html(import_string(pair[0]).__doc__ or "", indent=None),
                     sorted(pair[1].items(), key=lambda pair: __order__.index(pair[0]))),
                sorted(__endpoints__.items(),  key=lambda pair: __order__.index(pair[0]))))

def to_html(docstring, indent=4):
    if not indent is None:
        docstring = '\n'.join(map(lambda line: re.sub('^\s{%d}'%indent, '', line), docstring.split('\n')))
    return Markup(re.sub(r'^<div.*>|</div>$', '',publish_parts(
                docstring, writer_name='html',
                settings_overrides={'doctitle_xform':False})['html_body']))