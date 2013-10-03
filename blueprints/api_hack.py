__author__ = 'HansiHE'


from flask.signals import got_request_exception
from flask.ext.restful import Api
import sys
from werkzeug.http import HTTP_STATUS_CODES
import re
import difflib
from flask import request
from flask.ext.restful.utils import unauthorized, http_status_message


def error_data(code):
    error = {
        'error': [
            {
                'status': code,
                'message': http_status_message(code),
            }
        ]
    }
    return error


class RestfulApiCsrf(Api):


    def __init__(self, *args, **kwargs):
        self.csrf = kwargs.pop("csrf")
        super(RestfulApiCsrf, self).__init__(*args, **kwargs)

    def add_resource(self, resource, *urls, **kwargs):
        endpoint = kwargs.pop('endpoint', None) or resource.__name__.lower()
        self.endpoints.add(endpoint)

        if endpoint in self.app.view_functions.keys():
            previous_view_class = self.app.view_functions[endpoint].__dict__['view_class']

            # if you override the endpoint with a different class, avoid the collision by raising an exception
            if previous_view_class != resource:
                raise ValueError('This endpoint (%s) is already set to the class %s.' % (endpoint, previous_view_class.__name__))

        resource.mediatypes = self.mediatypes_method()  # Hacky
        resource.endpoint = endpoint
        resource_view = resource.as_view(endpoint) #MOD
        resource_func = self.output(resource_view) #MOD

        self.csrf.exempt(resource_view) #MOD

        for decorator in self.decorators:
            resource_func = decorator(resource_func)


        for url in urls:
            self.app.add_url_rule(self.prefix + url, view_func=resource_func, **kwargs)

    def handle_error(self, e):
        """Error handler for the API transforms a raised exception into a Flask
        response, with the appropriate HTTP status code and body.

        :param e: the raised Exception object
        :type e: Exception

        """
        got_request_exception.send(self.app, exception=e)

        if not hasattr(e, 'code') and self.app.propagate_exceptions:
            exc_type, exc_value, tb = sys.exc_info()
            if exc_value is e:
                exc = exc_type(exc_value)
                exc.__traceback__ = tb
                raise exc
            else:
                raise e

        code = getattr(e, 'code', 500)
        data = getattr(e, 'data', error_data(code))

        if code >= 500:

            # There's currently a bug in Python3 that disallows calling
            # logging.exception() when an exception hasn't actually be raised
            if sys.exc_info() == (None, None, None):
                self.app.logger.error("Internal Error")
            else:
                self.app.logger.exception("Internal Error")

        if code == 404 and ('message' not in data or
                            data['message'] == HTTP_STATUS_CODES[404]):
            rules = dict([(re.sub('(<.*>)', '', rule.rule), rule.rule)
                          for rule in self.app.url_map.iter_rules()])
            close_matches = difflib.get_close_matches(request.path, rules.keys())
            if close_matches:
                # If we already have a message, add punctuation and continue it.
                if "message" in data:
                    data["message"] += ". "
                else:
                    data["message"] = ""

                data['message'] += 'You have requested this URI [' + request.path + \
                        '] but did you mean ' + \
                        ' or '.join((rules[match]
                                     for match in close_matches)) + ' ?'

        resp = self.make_response(data, code)

        if code == 401:
            resp = unauthorized(resp,
                self.app.config.get("HTTP_BASIC_AUTH_REALM", "flask-restful"))

        return resp