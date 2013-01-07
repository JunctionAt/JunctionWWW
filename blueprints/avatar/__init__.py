__author__ = 'HansiHE'

from wtforms import Form, FileField, ValidationError
from wtforms.validators import *
import StringIO
from PIL import Image

class LoginForm(Form):
    image = FileField('New avatar', validators=[ Required() ])

    def validate_image(form, field):
        io = StringIO(field.data)
        loaded = Image.open(io)
        try:
            loaded.verify()
        except Exception:
            raise ValidationError("An error occurred while verifying the image.")