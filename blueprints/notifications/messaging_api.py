from flask_restful import Resource
from flask_restful.reqparse import RequestParser


class Messages(Resource):

    parser = RequestParser()

    def get(self):
        args = self.get_parser.parse_args()
        validate_args = self.validate_get(args)
        if validate_args:
            return validate_args