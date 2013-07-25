__author__ = 'HansiHE'

from flask.ext.restful import Resource
from flask.ext.restful.reqparse import RequestParser
from blueprints.auth import current_user


class InvalidDataException(Exception):
    pass

def get_bans(username=None, id=None, active=None, scope="local"):
    """

    :param username:
    :param id:
    :param active: none if both
    :param scope: local, global or full
    :return: array of bans
    """

    query = dict()

    if username:
        query["username"] = username
    if id:
        query["uid"] = id

    if not query.get("uid") and not query.get("username"):
        raise InvalidDataException()

    if active is not None:
        query["active"] = active




class Bans(Resource):

    get_parser = RequestParser()
    get_parser.add_argument("username", type=str)
    get_parser.add_argument("id", type=int)
    get_parser.add_argument("active", type=bool, default=True)
    get_parser.add_argument("scope", type=str, default="local", choices=["local", "global", "full"])

    def validate_get(self, args):
        if not args.get("username") and not args.get("id"):
            return {"message": "a id or a username must be provided"}, 400

    def get(self):
        args = self.get_parser.parse_args()
        validate_args = self.validate_get(args)
        if validate_args:
            return validate_args


    post_parser = RequestParser()
    post_parser.add_argument("username", type=str, required=True) # Username to ban
    post_parser.add_argument("issuer", type=str) # The one who created the ban, this is optional and requires extra permissions
    post_parser.add_argument("reason", type=str) # A optional reason for the ban
    post_parser.add_argument("location", type=str) # A optional server/interface where the ban was made

    def validate_post(self, args):
        if args.get("username") and len(args.get("username")) > 16:
            return {"message": "usernames are limited to 16 characters (username)"}, 400

        if args.get("issuer") and len(args.get("issuer")) > 16:
            return {"message": "usernames are limited to 16 characters (issuer)"}, 400
        if not args.get("issuer"):
            args["issuer"] = current_user.name

        if args.get("reason") and len(args.get("reason")) > 1000:
            return {"message": "the reason must be below 1000 characters long"}, 400

        if args.get("location") and len(args.get("location")) > 100:
            return {"message": "the location must be below 100 characters long"}

    def post(self):
        args = self.post_parser.parse_args()
        validate_args = self.validate_post(args)
        if validate_args:
            return validate_args


    delete_parser = RequestParser()
    delete_parser.add_argument("username", type=str)
    delete_parser.add_argument("id", type=int)

    def validate_delete(self, args):
        if not args.get("username") and not args.get("id"):
            return {"message": "a id or a username must be provided"}, 400

    def delete(self):
        args = self.delete_parser.parse_args()
        validate_args = self.validate_delete(args)
        if validate_args:
            return validate_args