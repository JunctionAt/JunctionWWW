__author__ = 'HansiHE'

from flask import Blueprint, request, render_template, abort, send_file, flash, redirect, url_for
from blueprints.auth import login_required
from avatar_model import Avatar
from flask_login import current_user
from flask_wtf import Form, FileField, SubmitField, ValidationError
import StringIO
import requests
from PIL import Image
import re

avatar = Blueprint('avatar', __name__, template_folder='templates')

mc_skin_url = 'http://s3.amazonaws.com/MinecraftSkins/%s.png'

class AvatarForm(Form):
    image = FileField('New avatar', validators=[ ])
    upload_button = SubmitField('Upload')
    mc_skin_button = SubmitField('Get skin face')

@avatar.route('/profile/avatar/', methods=["GET", "POST"])
@login_required
def avatar_control():

    form = AvatarForm()

    if request.method == "POST":
        if form.mc_skin_button.data:
            set_avatar(current_user.name, get_mc_face(current_user.name))
        elif form.upload_button.data and form.image.has_file():
            try:
                image = Image.open(StringIO.StringIO(form.image.data.read()))
                read_img = image.copy()
                image.verify()
            except IOError:
                return 'invalid image'

            read_img = read_img.resize((128, 128), Image.NEAREST) #TODO: Might want to change this for teh lookz
            out_image = StringIO.StringIO()
            read_img.save(out_image, "PNG")
            out_image.seek(0)
            #ret_data = out_image.getvalue()

            set_avatar(current_user.name, out_image)

    return render_template(
        'avatar_settings.html',
        avatar_form=form,
        name=current_user.name
    )

@avatar.route('/avatar/<string:name>.png')
def get_avatar(name):
    avatar = Avatar.objects(username=re.compile(name, re.IGNORECASE)).first()
    if avatar is None:
        return ""
    return send_file(avatar.image, mimetype='image/png')

def set_avatar(name, image):
    query = Avatar.objects(username=name)
    if len(query):
        entry = query.first()
        entry.image.replace(image)
        entry.save()
    else:
        entry = Avatar(username=name)
        entry.image.put(image)
        entry.save()

def get_mc_face(name):

    response = requests.get(mc_skin_url % name)

    if response.headers['content-type'] != 'application/octet-stream':
        return

    input = StringIO.StringIO(response.content)
    image = Image.open(input)

    image = image.crop((8,8,16,16))
    image = image.resize((128, 128), Image.NEAREST)

    out_img = StringIO.StringIO()
    image.save(out_img, "PNG")
    out_img.seek(0)

    return out_img