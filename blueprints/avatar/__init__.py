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
import os

from base64 import decodestring

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
    if avatar is None or avatar.image is None:
        return ""
    image = avatar.image
    ret = send_file(image, mimetype='image/png')
    return ret

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

def get_avatar_url(name):
    return url_for('avatar.get_avatar', name=name)

@avatar.route('/test.png')
def test_dump():
    str = StringIO.StringIO()
    str.write(decodestring("iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAAAAACPAi4CAAAACXBIWXMAAABIAAAASABGyWs+AAAACXZwQWcAAABAAAAAQADq8/hgAAAEaElEQVRYw82X6XLbNhCA+f4PVomk5MRyHDtp63oEgDcl3vfRBQhQIEVKSvsnO+OxRBEfFnthV+n/pyi/NaCryzzL8rJu/wOgzQPXJBgjhDExnXPW/Aqgy30DI0yIwYQQ4Bhe2j0I6BIbI1jL9meC2TdkRu0jgMxCGN5H2HT8IIzjKPAdE9NngEjuAhqfv3rOpe3aIrDAFoB1qtuA3ADlMXKuz9vlLqZokt4CxPAOQXa2bPDCRVSJYB0QIDA4ibp+TVKDbuCvAeh6YpX9DWkcUGJCkAARXW9UfXeL0PmUcF4CZBA4cALv5nqQM+yD4mtATQMOGMi9RzghiKriCuBiAzsB1e8uwUUGtroZIAEsqfqHCI2JjdGZHNDSZzHYb0boQK4JOTVXNQFEoJXDPskEvrYTrJHgIwOdZEBrggXzfkbo+sY7Hp0Fx9bUYbUEAAtgV/waHAcCnOew3arbLy5lVXGSXIrKGQkrKKMLcnHsPjEGAla1PYi+/YCV37e7DRp1qUDjwREK1wjbo56hezRoPLxt9lzUg+m96Hvtz3BMcU9syQAxKBSJ/c2Nqv0Em5C/97q+BdGoEuoORN98CkAqzsAAPh690vdv2tOOEcx/dodP0zq+qjpoQQF7/Vno2UA0OgLQQbUZI6t/1+BlRgAlyywvqtNXja0HFQ7jGVwoUA0HUBNcMvRdpW8PpzDPYRAERfmNE/TDuE8Ajis4oJAiUwB2+g+am3YEEmT5kz4HgOdRygHUIPEMsFf/YvXJYoSKbPczQI4HwysSbKKBdk4dLAhJsptrUHK1lSERUDYD6E9pGLsjoXzRZgAIJVaYBCCfA57zMBoJYfV9CXDigHhRgww2Hgngh4UjnCUbJAs2CEdCkl25kbou5ABh0KkXPupA6IB8fOUF4TpFOs5Eg50eFSOBfOz0GYCWoJwDoJzwcjQBfM2rMAjD0CEsL/Qp4ISG/FHkuJ4A9toXv66KomosMMNAuAA6GxOWPwqP64sb3kTm7HX1Fbsued9BXjACZKNIphLz/FF4WIps6vqff+jaIFAONiBbTf1hDITti5RLg+cYoDOxqJFwxb0dXmT5Bn/Pn8wOh9dQnMASK4aaSGuk+G24DObCbm5XzkXs9RdASTuytUZO6Czdm2BCA2cSgNbIWedxk0AV4FVYEYFJpLK4SuA3DrsceQEQl6svXy33CKfxIrwAanqZBA8R4AAQWeUMwJ6CZ7t7BIh6utfos0uLwxqP7BECMaTUuQCoawhO+9sSUWtjs1kA9I1Fm8DoNiCl64nUCsp9Ym1SgncjoLoz7YTl9dNOtbGRYSAjWbMDNPKw3py0otNeufVYN2wvzha5g6iGzlTDebsfEdbtW9EsLOvYZs06Dmbsq4GjcoeBgThBWtRN2zZ1mYUuGZ7axfz9hZEns+mMQ+ckzIYm/gn+WQvWWRq6uoxuSNi4RWWAYGfRuCtjXx25Bh25MGaTFzaccCVX1wfPtkiCk+e6nh/ExXps/N6z80PyL8wPTYgPwzDiAAAAJXRFWHRkYXRlOmNyZWF0ZQAyMDExLTAxLTE5VDAzOjU5OjAwKzAxOjAwaFry6QAAACV0RVh0ZGF0ZTptb2RpZnkAMjAxMC0xMi0yMVQxNDozMDo0NCswMTowMGxOe/8AAAAZdEVYdFNvZnR3YXJlAEFkb2JlIEltYWdlUmVhZHlxyWU8AAAAAElFTkSuQmCC"))
    str.seek(0)
    return send_file(str, mimetype='image/png')