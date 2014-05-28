from blueprints.auth import current_user, login_required
from flask import abort, render_template, request, url_for, flash, redirect, session, Response
from flask_wtf import Form
from wtforms.fields import StringField
from wtforms.validators import InputRequired, Length
import base64
import binascii
import qrcode
import random
from oath import accept_totp
from StringIO import StringIO
from urllib import quote, urlencode

from .. import blueprint
from . import add_settings_pane, settings_panels_structure
from models.user_model import User


def _totp_url(secret=None):
    return 'otpauth://totp/{issuer}:{account}?{params}'.format(
        issuer='Junction',
        account=quote(current_user.name),
        params=urlencode({
            'issuer': 'Junction',
            'secret': secret or current_user.tfa_secret
        }))


class TOTPSetupForm(Form):
    code = StringField('Verification Code', [InputRequired("The verification code is required."),
                                             Length(min=6, max=6, message="Invalid code length.")])


class TOTPDisableForm(Form):
    pass


@blueprint.route('/settings/tfa')
@login_required
def tfa_pane():
    form = TOTPDisableForm(request.form)
    return render_template('settings_tfa.html', current_user=current_user,
                           settings_panels_structure=settings_panels_structure,
                           form=form, title="TFA - Account - Settings")


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
        abort(403)

    text = session['tfa-new-secret']
    readable = ' '.join(text[i:i + 4] for i in range(0, len(text), 4))

    return render_template('settings_tfa_enable.html', current_user=current_user,
                           settings_panels_structure=settings_panels_structure,
                           secret=readable, form=form, title="TFA - Account - Settings",
                           totp_url=_totp_url(secret=session['tfa-new-secret']))


@blueprint.route('/settings/tfa/viewkey')
@login_required
def tfa_viewkey():
    if not current_user.tfa:
        abort(401)
    text = current_user.tfa_secret
    readable = ' '.join(text[i:i + 4] for i in range(0, len(text), 4))
    return render_template('settings_tfa_viewkey.html', current_user=current_user,
                           settings_panels_structure=settings_panels_structure,
                           secret=readable, title="TFA - Account - Settings",
                           totp_url=_totp_url())


@blueprint.route('/settings/tfa/qrcode.png', defaults={'new': False, 'small': False})
@blueprint.route('/settings/tfa/qrcode/small.png', defaults={'new': False, 'small': True})
@blueprint.route('/settings/tfa/qrcode/new.png', defaults={'new': True, 'small': False})
@blueprint.route('/settings/tfa/qrcode/new/small.png', defaults={'new': True, 'small': True})
@login_required
def tfa_qrcode(new, small):
    if new:
        if session.get('tfa-new-method', None) != 'TOTP':
            abort(401)
        url = _totp_url(secret=session['tfa-new-secret'])
    else:
        if current_user.tfa_method != 'TOTP':
            abort(401)
        url = _totp_url(secret=current_user.tfa_secret)
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
    form = TOTPDisableForm(request.form)
    if form.validate():
        current_user.tfa = False
        current_user.tfa_method = ''
        current_user.tfa_secret = ''
        current_user.tfa_info = ''
        current_user.save()
    return redirect(url_for('settings.tfa_pane')), 303


add_settings_pane(lambda: url_for('settings.tfa_pane'), "Account", "Two-Factor Auth")


@blueprint.route("/p/<string:name>/resettfa", defaults={'confirmed': "no"})
@blueprint.route("/p/<string:name>/resettfa/<string:confirmed>")
@login_required
def reset_tfa(name, confirmed):
    if not current_user.has_permission('auth.reset_tfa'):
        abort(403)

    if confirmed != "yes":
        return "<a href=" + url_for('settings.reset_tfa', name=name, confirmed="yes") + ">click here to confirm tfa reset</a>"

    user = User.objects(name=name).first()
    if user is None:
        abort(404)

    user.tfa = False
    user.tfa_method = ''
    user.tfa_secret = ''
    user.tfa_info = None
    user.save()

    return "success"
