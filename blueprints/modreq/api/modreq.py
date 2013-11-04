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


def get_modreqs(uid=None, status=None, username=None):
    query = dict()

    if uid is not None:
        query['uid'] = uid
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
        playerName=modreq.username,
        request=modreq.request,
        location=modreq.location,
        status=modreq.status,
        openTime=modreq.time.strftime(datetime_format) if modreq.time is not None else None,
        handledBy=modreq.handled_by,
        closeMessage=modreq.close_message,
        closeTime=modreq.close_time.strftime(datetime_format) if modreq.close_time is not None else None)


class ModReq(Resource):
    get_parser = RequestParser()
    get_parser.add_argument("id", type=int)
    get_parser.add_argument("status", type=str, choices=["open", "claimed", "closed"])
    get_parser.add_argument("playerName", type=str)

    def validate_get(self, args):
        if args.get("playerName") and not validate_username(args.get("playerName")):
            return {'error': [{"message": "invalid playerName"}]}

        if not any([args.get("playerName"), args.get("status"), args.get("id")]):
            return {'error': [{"message": "an id, a status, or a playerName must be provided"}]}

    #@require_api_key(access_tokens=['modreq.get'])
    @endpoint()
    def get(self):
        args = self.get_parser.parse_args()
        validate_args = self.validate_get(args)
        if validate_args:
            return validate_args, 400

        uid = args.get("id")
        status = args.get("status")
        username = args.get("playerName")

        modreqs = get_modreqs(uid, status, username)

        return {'modreqs': modreqs}

    post_parser = RequestParser()
    post_parser.add_argument("playerName", type=str, required=True)
    post_parser.add_argument("request", type=str, required=True)
    post_parser.add_argument("location", type=str, required=True)

    def validate_post(self, args):
        if args.get("playerName") and not validate_username(args.get("playerName")):
            return {'error': [{"message": "invalid playerName"}]}

        if args.get("request") and len(args.get("request")) > 1000:
            return {'error': [{"message": "the request must be below 1000 characters long"}]}

        if args.get("location") and len(args.get("location")) > 100:
            return {'error': [{"message": "the location must be below 100 characters long"}]}

    @require_api_key(access_tokens=['modreq.add'])
    @endpoint()
    def post(self):
        args = self.post_parser.parse_args()
        validate_args = self.validate_post(args)
        if validate_args:
            return validate_args, 400

        username = args.get("playerName")
        request = args.get("request")
        location = args.get("location")

        modreq = ModReqModel(username=username, request=request, location=location, status="open").save()

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
    post_parser.add_argument("id", type=int, required=True)
    post_parser.add_argument("handledBy", type=str, required=True)
    post_parser.add_argument("closeMessage", type=str, required=True)

    def validate_post(self, args):
        if args.get("handledBy") and not validate_username(args.get("handledBy")):
            return {'error': [{"message": "invalid handledBy"}]}

        if args.get("closeMessage") and len(args.get("closeMessage")) > 1000:
            return {'error': [{"message": "the closeMessage must be below 1000 characters long"}]}

        if not args.get("handledBy") or not args.get("id"):
            return {'error': [{"message": "an id and a handledBy must be provided"}]}

    @require_api_key(access_tokens=['modreq.done'])
    @endpoint()
    def post(self, modreq_id):
        args = self.post_parser.parse_args()
        validate_args = self.validate_post(args)
        if validate_args:
            return validate_args, 400

        handled_by = args.get("handledBy")
        close_message = args.get("closeMessage")

        modreq = ModReqModel.objects(uid=modreq_id).first()

        modreq.status = "closed"
        modreq.handled_by = handled_by
        modreq.close_message = close_message
        modreq.close_time = datetime.datetime.utcnow()
        modreq.save()

        return {'modreq': construct_modreq_data(modreq)}


rest_api.add_resource(ModReq, '/modreq')
rest_api.add_resource(ModReqClaim, '/modreq/<int:modreq_id>/claim')
rest_api.add_resource(ModReqDone, '/modreq/<int:modreq_id>/done')

register_api_access_token("modreq.get", permission="api.modreq.get")
register_api_access_token("modreq.add", permission="api.modreq.add")
register_api_access_token("modreq.claim", permission="api.modreq.claim")
register_api_access_token("modreq.done", permission="api.modreq.done")
