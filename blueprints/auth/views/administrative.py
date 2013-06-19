__author__ = 'HansiHE'

import datetime

from flask_login import current_user
from flask import abort, jsonify

from blueprints.api import apidoc
from .. import blueprint, login_required
#from ..user_model import Token


#@apidoc(__name__, blueprint, '/token/<player>.json', defaults=dict(ext='json'))
#@login_required
#def get_token(player, ext):
#    """
#    Used by staff to get the activation token for ``player``.
#    """
#
#    if not current_user.has_permission("auth.get_token"):
#        abort(403)
#
#    token = Token.objects(name=player, expires__gte=datetime.datetime.utcnow()).order_by("-expires").first()
#    if token:
#        return jsonify(token=token.token)
#    else:
#        abort(404)