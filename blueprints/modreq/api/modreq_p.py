__author__ = 'williammck'

from flask import request
from blueprints.api import require_api_key, register_api_access_token, datetime_format
from blueprints.base import rest_api
from flask.ext.restful import Resource
from flask.ext.restful.reqparse import RequestParser
from ..modreq_model import ModReqP
import re
from blueprints.auth.util import validate_username
import datetime


def get_modreqs(uid=None, status=None, username=None):
    query = dict()

    if uid is not None:
        query['uid'] = uid
    if status is not None:
        query['status'] = status
    if username is not None:
        query['username'] = re.compile(username, re.IGNORECASE)

    modreqs_data = ModReqP.objects(**query)

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


class ModReq_P(Resource):
    get_parser = RequestParser()
    get_parser.add_argument("id", type=int)
    get_parser.add_argument("status", type=str, choices=["open", "claimed", "closed"])
    get_parser.add_argument("playerName", type=str)

    def validate_get(self, args):
        if args.get("playerName") and not validate_username(args.get("playerName")):
            return {'error': [{"message": "invalid playerName"}]}

        if not any([args.get("playerName"), args.get("status"), args.get("id")]):
            return {'error': [{"message": "an id, a status, or a playerName must be provided"}]}

    @require_api_key(access_tokens=['modreq.p'])
    def get(self):
        args = self.get_parser.parse_args()
        validate_args = self.validate_get(args)
        if validate_args:
            return validate_args

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

    @require_api_key(access_tokens=['modreq.p'])
    def post(self):
        args = self.post_parser.parse_args()
        validate_args = self.validate_post(args)
        if validate_args:
            return validate_args

        username = args.get("playerName")
        request = args.get("request")
        location = args.get("location")

        modreq = ModReqP(username=username, request=request, location=location, status="open").save()

        return {'modreq': construct_modreq_data(modreq)}


class ModReq_P_Claim(Resource):
    post_parser = RequestParser()
    post_parser.add_argument("id", type=int, required=True)
    post_parser.add_argument("handledBy", type=str, required=True)

    def validate_post(self, args):
        if args.get("handledBy") and not validate_username(args.get("handledBy")):
            return {'error': [{"message": "invalid handledBy"}]}

        if not args.get("handledBy") or not args.get("id"):
            return {'error': [{"message": "an id and a handledBy must be provided"}]}

    @require_api_key(access_tokens=['modreq.p'])
    def post(self):
        args = self.post_parser.parse_args()
        validate_args = self.validate_post(args)
        if validate_args:
            return validate_args

        uid = args.get("id")
        handled_by = args.get("handledBy")

        modreq = ModReqP.objects(uid=uid).first()

        modreq.status = "claimed"
        modreq.handled_by = handled_by
        modreq.save()

        return {'modreq': construct_modreq_data(modreq)}

class ModReq_P_UnClaim(Resource):
    post_parser = RequestParser()
    post_parser.add_argument("id", type=int, required=True)

    def validate_post(self, args):
        if not args.get("id"):
            return {'error': [{"message": "an id must be provided"}]}

    @require_api_key(access_tokens=['modreq.p'])
    def post(self):
        args = self.post_parser.parse_args()
        validate_args = self.validate_post(args)
        if validate_args:
            return validate_args

        uid = args.get("id")

        modreq = ModReqP.objects(uid=uid).first()

        modreq.status = "open"
        modreq.handled_by = ""
        modreq.save()

        return {'modreq': construct_modreq_data(modreq)}


class ModReq_P_Done(Resource):
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

    @require_api_key(access_tokens=['modreq.p'])
    def post(self):
        args = self.post_parser.parse_args()
        validate_args = self.validate_post(args)
        if validate_args:
            return validate_args

        uid = args.get("id")
        handled_by = args.get("handledBy")
        close_message = args.get("closeMessage")

        modreq = ModReqP.objects(uid=uid).first()

        modreq.status = "closed"
        modreq.handled_by = handled_by
        modreq.close_message = close_message
        modreq.close_time = datetime.datetime.utcnow()
        modreq.save()

        return {'modreq': construct_modreq_data(modreq)}


rest_api.add_resource(ModReq_P, '/modreq/p')
rest_api.add_resource(ModReq_P_Claim, '/modreq/p/claim')
rest_api.add_resource(ModReq_P_UnClaim, '/modreq/p/unclaim')
rest_api.add_resource(ModReq_P_Done, '/modreq/p/done')

register_api_access_token("modreq.p", permission="api.modreq.p")
