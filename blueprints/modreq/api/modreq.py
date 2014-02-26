__author__ = 'williammck'

from flask import request
from blueprints.api import require_api_key, register_api_access_token, datetime_format, endpoint
from blueprints.base import rest_api
from flask.ext.restful import Resource
from flask.ext.restful.reqparse import RequestParser
from ..modreq_model import ModReq as ModReqModel
import re
from blueprints.auth.util import validate_username
import datetime

from flask.ext.wtf import Form
from wtforms.fields import StringField, BooleanField
#from wtforms.validators import
from blueprints.form_validators import RequiredIf


def get_modreqs(uid=None, server=None, status=None, username=None):
    query = dict()

    if uid is not None:
        query['uid'] = uid
    if server is not None:
        query['server'] = server
    if status is not None:
        query['status'] = status
    if username is not None:
        query['username'] = re.compile(username, re.IGNORECASE)

    modreqs_data = ModReqModel.objects(**query)

    modreqs_response = []
    for modreq_data in modreqs_data:
        modreqs_response.append(construct_modreq_data(modreq_data))

    return modreqs_response


def construct_modreq_data(modreq):
    return dict(
        id=modreq.uid,
        server=modreq.server,
        username=modreq.username,
        request=modreq.request,
        location=modreq.location,
        status=modreq.status,
        time=modreq.time.strftime(datetime_format) if modreq.time is not None else None,
        handled_by=modreq.handled_by,
        close_message=modreq.close_message,
        close_time=modreq.close_time.strftime(datetime_format) if modreq.close_time is not None else None)


class ModReq(Resource):
    get_parser = RequestParser()
    get_parser.add_argument("id", type=int)
    get_parser.add_argument("server", type=str)
    get_parser.add_argument("status", type=str, choices=["open", "elevated", "claimed", "closed"])
    get_parser.add_argument("username", type=str)

    def validate_get(self, args):
        if args.get("username") and not validate_username(args.get("username")):
            return {'error': [{"message": "invalid username"}]}

        # need server logic

        if not any([args.get("username"), args.get("status"), args.get("server"), args.get("id")]):
            return {'error': [{"message": "an id, a server, a status, or a username must be provided"}]}

    @require_api_key(access_tokens=['modreq.get'])
    @endpoint()
    def get(self):
        args = self.get_parser.parse_args()
        validate_args = self.validate_get(args)
        if validate_args:
            return validate_args, 400

        uid = args.get("id")
        server = args.get("server")
        status = args.get("status")
        username = args.get("username")

        modreqs = get_modreqs(uid, server, status, username)

        return {'modreqs': modreqs}

    post_parser = RequestParser()
    post_parser.add_argument("username", type=str, required=True)
    post_parser.add_argument("request", type=str, required=True)
    post_parser.add_argument("server", type=str, required=True)
    post_parser.add_argument("location", type=str, required=True)

    def validate_post(self, args):
        if args.get("username") and not validate_username(args.get("username")):
            return {'error': [{"message": "invalid username"}]}

        # need server logic

        if args.get("request") and len(args.get("request")) > 1000:
            return {'error': [{"message": "the request must be below 1000 characters long"}]}

        if args.get("server") and len(args.get("server")) > 10:
            return {'error': [{"message": "the server must be below 10 characters long"}]}

        if args.get("location") and len(args.get("location")) > 100:
            return {'error': [{"message": "the location must be below 100 characters long"}]}

    @require_api_key(access_tokens=['modreq.add'])
    @endpoint()
    def post(self):
        args = self.post_parser.parse_args()
        validate_args = self.validate_post(args)
        if validate_args:
            return validate_args, 400

        username = args.get("username")
        request = args.get("request")
        server = args.get("server")
        location = args.get("location")

        modreq = ModReqModel(username=username, request=request, server=server, location=location, status="open").save()

        return {'modreq': construct_modreq_data(modreq)}


class ModReqClaim(Resource):
    post_parser = RequestParser()
    post_parser.add_argument("claim", type=bool, required=True)
    post_parser.add_argument("handled_by", type=str)

    def validate_post(self, args):
        if args.get("claim"):
            if not args.get("handled_by"):
                return {'error': [{"message": "handled_by must be provided when claim=true"}]}

            if not validate_username(args.get("handled_by")):
                return {'error': [{"message": "handled_by must be a valid minecraft username"}]}

    @require_api_key(access_tokens=['modreq.claim'])
    @endpoint()
    def post(self, modreq_id):
        args = self.post_parser.parse_args()
        validate_args = self.validate_post(args)
        if validate_args:
            return validate_args, 400

        claim = args.get("claim")
        handled_by = args.get("handled_by")

        modreq = ModReqModel.objects(uid=modreq_id).first()

        if claim:
            pass
        else:
            pass

        modreq.status = "claimed"
        modreq.handled_by = handled_by
        modreq.save()

        return {'modreq': construct_modreq_data(modreq)}


class ModReqDone(Resource):
    post_parser = RequestParser()
    post_parser.add_argument("handled_by", type=str, required=True)
    post_parser.add_argument("close_message", type=str, required=True)

    def validate_post(self, args):
        if args.get("handled_by") and not validate_username(args.get("handled_by")):
            return {'error': [{"message": "invalid handled_by"}]}

        if args.get("close_message") and len(args.get("close_message")) > 1000:
            return {'error': [{"message": "the close_message must be below 1000 characters long"}]}

    @require_api_key(access_tokens=['modreq.done'])
    @endpoint()
    def post(self, modreq_id):
        args = self.post_parser.parse_args()
        validate_args = self.validate_post(args)
        if validate_args:
            return validate_args, 400

        handled_by = args.get("handled_by")
        close_message = args.get("close_message")

        modreq = ModReqModel.objects(uid=modreq_id).first()

        modreq.status = "closed"
        modreq.handled_by = handled_by
        modreq.close_message = close_message
        modreq.close_time = datetime.datetime.utcnow()
        modreq.save()

        return {'modreq': construct_modreq_data(modreq)}

class ModReqElevate(Resource):
    post_parser = RequestParser()
    post_parser.add_argument("group", type=str, required=True)

    def validate_post(self, args):
        if not args.get("group"):# need group verification logic!
            return {'error': [{"message": "invalid group"}]}

    @require_api_key(access_tokens=['modreq.elevate'])
    @endpoint()
    def post(self, modreq_id):
        args = self.post_parser.parse_args()
        validate_args = self.validate_post(args)
        if validate_args:
            return validate_args, 400

        group = args.get("group")

        modreq = ModReqModel.objects(uid=modreq_id).first()

        modreq.status = "elevated"
        modreq.group = group
        modreq.save()

        return {'modreq': construct_modreq_data(modreq)}


rest_api.add_resource(ModReq, '/modreq')
rest_api.add_resource(ModReqClaim, '/modreq/<int:modreq_id>/claim')
rest_api.add_resource(ModReqDone, '/modreq/<int:modreq_id>/done')
rest_api.add_resource(ModReqElevate, '/modreq/<int:modreq_id>/elevate')

register_api_access_token("modreq.get", permission="api.modreq.get")
register_api_access_token("modreq.add", permission="api.modreq.add")
register_api_access_token("modreq.claim", permission="api.modreq.claim")
register_api_access_token("modreq.done", permission="api.modreq.done")
register_api_access_token("modreq.elevate", permission="api.modreq.elevate")
