__author__ = 'zifnab06'

from flask import request
from flask.ext.restful import Resource
from flask.ext.restful.reqparse import RequestParser
import re

from blueprints.api import require_api_key, register_api_access_token, datetime_format
from blueprints.base import rest_api
from blueprints.auth.util import validate_username
from models.servers_model import Server
from models.ban_model import Note


class InvalidDataException(Exception):
    pass

def get_local_notes(username=None, uid=None, active=None):
    query = dict()

    if username is not None:
        query['username'] = re.compile(username, re.IGNORECASE)
    if uid is not None:
        query['uid'] = uid
    if active is not None:
        query['active'] = active

    notes_data = Note.objects(**query)

    notes_response = []

    for note_data in notes_data:
        notes_response.append(construct_local_note_data(note_data))

    return notes_response

def construct_local_note_data(note):
    return dict(
        id = note.uid, issuer = note.issuer, username = note.username,
        server = note.server,
        time = note.time.strftime(datetime_format) if note.time is not None else None,
        active = note.active,
        note = note.note
    )

def get_global_notes(username):
    return [] #NYI

def get_notes(username=None, uid=None, active=None, scope="local"):
    """
    :param username:
    :param uid:
    :param active: none if both:
    :param scope: local, global or full
    :return: array of notes:
    """
    notes_raw = list()

    if scope == 'local' or scope == 'full':
        notes_raw += get_local_notes(username=username, uid=uid, active=active)
    elif scope == 'global' or scope == 'full':
        notes_raw += get_global_notes(username=username)

    return notes_raw

class Notes(Resource):
    get_parser = RequestParser()
    get_parser.add_argument("username", type=str)
    get_parser.add_argument("id", type=int)
    get_parser.add_argument("scope", type=str, default="local", choices=["local", "global", "full"])
    get_parser.add_argument("scope", type=str, default="local", choices=["local", "global", "full"])

    def validate_get(self, args):
        if not args.get("username") and not args.get("id"):
            return {'error': [{"message": "an id or a username must be provided"}]}

        if args.get("id" and args.get("scope" != "local")):
            return {'error': [{"message": "query by id can only be used in local scope"}]}

        if args.get("active") == "False" and args.get("scope") != "local":
            return {'error': [{"message": "query for non active bans can only be used in local scope"}]}

    @require_api_key(required_access_tokens=['anathema.notes.get'], asuser_must_be_registered=False)
    def get(self):
        args = self.get_parser.parse_args()
        validate_args = self.validate_get(args)
        if validate_args:
            return validate_args

        username = args.get("username")
        uid = args.get("id")

        active_str = args.get("active")
        active = None
        if active_str != 'none':
            if active_str == 'true':
                active = True
            elif active_str == 'false':
                active = False

        scope = args.get("scope")

        notes = get_notes(username, uid, active, scope)

        return {'notes': notes}

    post_parser = RequestParser()
    post_parser.add_argument("username", type=str, required=True) #username to add note to
    post_parser.add_argument("note", type=str, required=True) #required note mesasge
    post_parser.add_argument("server", type=str, required=True) #required server note was made on

    def validate_post(selfself, args):
        if args.get("username") and not validate_username(args.get("username")):
            return {'error': [{"message": "invalid username"}]}

        if args.get("note") and len(args.get("note")) > 1000:
            return {'error': [{"message": "the note must be below 1000 characters long"}]}

        if args.get("server") and Server.verify_fid(args.get("server")): #len(args.get("server")) > 10:
            return {'error': [{"message": "the location must be below 10 characters long"}]}

    @require_api_key(required_access_tokens=['anathema.notes.post'], asuser_must_be_registered=False)
    def post(self):
        args = self.post_parser.parse_args()
        validate_args = self.validate_post(args)
        if validate_args:
            return validate_args

        issuer = request.api_user_name
        username = args.get("username")
        note = args.get("note")
        source = args.get("server")

        note = Note(issuer=issuer, username=username, note=note, server=source).save()
        return {'note': construct_local_note_data(note)}


rest_api.add_resource(Notes, '/anathema/notes')

register_api_access_token('anathema.notes.get', permission='api.anathema.notes.get')
register_api_access_token('anathema.notes.post', permission='api.anathema.notes.post')

