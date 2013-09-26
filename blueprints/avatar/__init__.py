__author__ = 'HansiHE'

from flask import Blueprint, request, render_template, abort, send_file, flash, redirect, url_for, current_app
from blueprints.auth import login_required
from avatar_model import Avatar
from flask_login import current_user
from flask_wtf import Form, FileField, SubmitField
import StringIO
import requests
from PIL import Image
import re
import os
import mongoengine
from datetime import datetime
import flask
from blueprints.settings.views import settings_panels_structure

from base64 import decodestring

avatar = Blueprint('avatar', __name__, template_folder='templates')

mc_skin_url = 'http://s3.amazonaws.com/MinecraftSkins/%s.png'


class AvatarForm(Form):
    image = FileField('New avatar', validators=[ ])
    upload_button = SubmitField('Upload')
    mc_skin_button = SubmitField('Get skin face')


@avatar.route('/settings/avatar', methods=["GET", "POST"])
@login_required
def avatar_control():
    form = AvatarForm()

    if request.method == "POST":
        if form.mc_skin_button.data:
            set_avatar(current_user.name, get_mc_face(current_user.name))
        elif form.upload_button.data and form.image.has_file():
            try:
                data = StringIO.StringIO(form.image.data.read())
                image = Image.open(data)
                image.verify()

                data.seek(0)
                read_img = Image.open(data)
                #image.verify()
            except IOError:
                return 'invalid image'

            read_img = read_img.resize((128, 128), Image.NEAREST) #TODO: Might want to change this for teh lookz
            out_image = StringIO.StringIO()
            read_img.save(out_image, "PNG")
            out_image.seek(0)
            #ret_data = out_image.getvalue()

            set_avatar(current_user.name, out_image)

        return redirect(request.path)

    return render_template(
        'avatar_pane.html',
        settings_panels_structure=settings_panels_structure,
        avatar_form=form,
        name=current_user.name,
        user=current_user
    )


def set_mc_face_as_avatar(user):
    return set_avatar(user, get_mc_face(user))


def get_avatar_url(name):
    return url_for('avatar.get_avatar', name=name)


@avatar.route('/avatar/<string:name>.png')
def get_avatar(name):
    avatar = Avatar.objects(username=re.compile(name, re.IGNORECASE)).first()
    if avatar is None or avatar.image is None:
        return send_file(open('blueprints/avatar/char_face.png', 'r'), mimetype='image/png',
                         cache_timeout=3600 * 24 * 30, add_etags=False)
    else:
        if not avatar.last_modified or not request.if_modified_since or avatar.last_modified > request.if_modified_since:
            image = StringIO.StringIO(avatar.image.read())
            image.seek(0)
            response = send_file(image, mimetype='image/png')
            response.last_modified = avatar.last_modified
            response.expires = None
            return response
        else:
            return flask.Response(status=304)


@avatar.route('/avatar/reset/<username>')
@login_required
def set_mc_face_as_avatar_request(username):
    if not current_user.has_permission("avatar.reset"):
        abort(401)
    return str(set_mc_face_as_avatar(username))


def set_avatar(name, image):
    if not image:
        return False

    entry = Avatar.objects(username=name).first()
    try:
        if entry:
            entry.image.replace(image)
            entry.last_modified = datetime.utcnow().replace(microsecond=0)
            entry.save()
        else:
            entry = Avatar(username=name)
            entry.image.put(image)
            entry.save()
    except mongoengine.ValidationError:
        return False

    return True


def get_mc_face(name):

    response = requests.get(mc_skin_url % name)

    if response.headers['content-type'] != 'application/octet-stream':
        return

    if response.status_code != 200:
        return

    # noinspection PyShadowingBuiltins
    input = StringIO.StringIO(response.content)
    image = Image.open(input)

    image = image.crop((8,8,16,16))
    image = image.resize((128, 128), Image.NEAREST)

    out_img = StringIO.StringIO()
    image.save(out_img, "PNG")
    out_img.seek(0)

    return out_img

import avatar_settings_pane