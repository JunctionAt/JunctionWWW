from blueprints.base import csrf
from blueprints.auth import current_user, login_required
from flask import abort, render_template, request, url_for, flash, redirect, current_app, session, send_file, Response
from flask_wtf import Form
from wtforms.fields import TextField
from wtforms.validators import Required, Length
from .. import blueprint
from . import add_settings_pane, settings_panels_structure

import base64
import binascii
import oath
import qrcode
import random
from oath import accept_totp
from StringIO import StringIO
from urllib import quote, urlencode


class TOTPSetupForm(Form):
    code = TextField('Verification Code', [Required("The verification code is required."),
                                           Length(min=6, max=6, message="Invalid code length.")])


@blueprint.route('/settings/tfa')
@login_required
def tfa_pane():
    enabled = current_user.tfa
    return render_template('settings_tfa.html', current_user=current_user,
                            settings_panels_structure=settings_panels_structure,
                            title="TFA - Account - Settings")


@blueprint.route('/settings/tfa/enable', methods=['GET', 'POST'])
@login_required
def tfa_enable():
    form = TOTPSetupForm(request.form)

    if request.method == "GET":
        # generate a new secret
        secret = ''
        rand = random.SystemRandom()
        for i in range(30):
            secret += chr(rand.getrandbits(8))
        session['tfa-new-method'] = 'TOTP'
        session['tfa-new-secret'] = base64.b32encode(secret)
    elif request.method == "POST" and form.validate():
        method = session.get('tfa-new-method', None)
        if method == 'TOTP':
            # check code
            key = binascii.hexlify(base64.b32decode(session['tfa-new-secret']))
            ok, drift = accept_totp(format='dec6', key=key, response=form.code.data)
            if not ok:
                form.errors['tfa'] = ['Verification error, please try again.']
            else:
                current_user.tfa = True
                current_user.tfa_method = 'TOTP'
                current_user.tfa_secret = session['tfa-new-secret']
                current_user.tfa_info['drift'] = drift
                current_user.save()
                del session['tfa-new-method']
                del session['tfa-new-secret']
                flash('Two-Factor Authentication enabled', category='success')
                return redirect(url_for('settings.tfa_pane')), 303
        else:
            abort(401)
    else:
        # bad
        pass

    text = session['tfa-new-secret']
    readable = ' '.join(text[i:i+4] for i in range(0, len(text), 4))

    return render_template('settings_tfa_enable.html', current_user=current_user,
                           settings_panels_structure=settings_panels_structure,
                           secret=readable, form=form, title="TFA - Account - Settings")


@blueprint.route('/settings/tfa/qrcode.png', defaults={'small': False})
@blueprint.route('/settings/tfa/qrcode/small.png', defaults={'small': True})
@login_required
def tfa_qrcode(small):
    if session.get('tfa-new-method', None) != 'TOTP':
        abort(401)
    url = 'otpauth://totp/{issuer}:{account}?{params}'.format(
            issuer='Junction',
            account=quote(current_user.name),
            params=urlencode({
                'issuer': 'Junction',
                'secret': session['tfa-new-secret']
            }))
    if small:
        qr = qrcode.make(url, box_size=4, border=4,
                         error_correction=qrcode.constants.ERROR_CORRECT_L)
    else:
        qr = qrcode.make(url, box_size=8, border=1)
    io = StringIO()
    qr.save(io, 'png')
    return Response(io.getvalue(), mimetype='image/png')


@blueprint.route('/settings/tfa/disable', methods=['POST'])
@login_required
def tfa_disable():
    current_user.tfa = False
    current_user.tfa_secret = ''
    current_user.save()
    return redirect(url_for('settings.tfa_pane')), 303


add_settings_pane(lambda: url_for('settings.tfa_pane'), "Account", "Two-Factor Auth")
