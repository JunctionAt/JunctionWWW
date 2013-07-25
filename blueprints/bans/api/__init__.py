__author__ = 'HansiHE'

from flask import current_app


rest_api = current_app.rest_api

import bans, notes

rest_api.add_resource(bans.Bans, '/anathema/bans/')
rest_api.add_resource(notes.Notes, '/anathema/notes/')