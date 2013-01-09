__author__ = 'HansiHE'

from flask import Blueprint
from blueprints.auth import login_required
from wtforms import Form, FileField, ValidationError
from wtforms.validators import *
import StringIO
from PIL import Image

avatar = Blueprint('avatar', __name__, template_folder='templates')

class LoginForm(Form):
    image = FileField('New avatar', validators=[ Required() ])

    def validate_image(form, field):
        io = StringIO(field.data)
        loaded = Image.open(io)
        try:
            loaded.verify()
        except Exception:
            raise ValidationError("An error occurred while verifying the image.")

@avatar.route('/profile/avatar/')
@login_required
def avatar_control():
    pass