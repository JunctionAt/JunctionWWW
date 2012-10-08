"""
Junction.at/api
===============

This document describes the API to the Junction site and Minecraft servers.

Authorization
-------------
You may use a cookie or HTTP Basic Auth for authorization.
You must have a registered and verified Junction.at user account to make requests that require authorization.

URI Arguments
--------------
All URIs and arguments are case-sensitive.  The server will redirect to the preffered capitalization of these resources with a 301 status code.

For many resources, you must specify a <server>. Possible values for <server> are ``pve``, ``survival``, ``creative``, and ``event``.

JSON
----
All resources have a .json extension and will respond with JSON data on success, either in the initial response body or through another resource via redirect.

Data provided in a request body must be either form or JSON encoded. JSON data must include a ``Content-Type: application/json`` request header.

Status Codes
------------

General rules for how status codes are used by the API:

200
    Resource found. The response body will be JSON data.

301
    Resource can be found at preferred URI. Do not use this URI for future requests. Send the same request to provided URI to complete operation.

302
    Resource found or assertion succeeded. Follow redirect with a GET request for relevant JSON data.

303
    Operation successful. You may follow the redirect with a GET request, but is not guaranteed to return a successful status code depending on the operation performed.

400
    Operation unsuccessfull. Relevant JSON data will be provided in the response body.

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
        methods = endpoints.get(self.rule, list())
        endpoints[self.rule] = methods
        if not self.rule in __order__: __order__ += [self.rule]
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
                    (re.sub(r'^.*_', '', pair[0].split('.')[-1]).capitalize(),
                     to_html(import_string(pair[0]).__doc__ or "", indent=None),
                     sorted(pair[1].items(), key=lambda pair: __order__.index(pair[0]))),
                sorted(__endpoints__.items(),  key=lambda pair: __order__.index(pair[0]))))

def to_html(docstring, indent=4):
    if not indent == None:
        docstring = '\n'.join(map(lambda line: re.sub('^\s{%d}'%indent, '', line), docstring.split('\n')))
    return Markup(re.sub(r'^<div.*>|</div>$', '',publish_parts(
                docstring, writer_name='html',
                settings_overrides={'doctitle_xform':False})['html_body']))
