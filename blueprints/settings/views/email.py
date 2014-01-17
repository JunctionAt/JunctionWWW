__author__ = 'HansiHE'

from flask import render_template, request, url_for, abort, flash, redirect
from .. import blueprint
from flask_wtf import Form
from wtforms.fields import TextField, SubmitField
from wtforms.validators import Email, Required, InputRequired
from blueprints.auth import current_user, User, login_required
from blueprints.base import mail
from flask.ext.mail import Message
from itsdangerous import URLSafeSerializer
import datetime, time
from . import add_settings_pane, settings_panels_structure


serializer = URLSafeSerializer('kjF4IvN6fuFeAKrSTlvTsIR6nZZOuhw5SKEox0goL8KEwo8AMF')


class EmailUpdateForm(Form):

    mail = TextField('Email address', validators=[Required('Please enter a Email address.'),
                                                  InputRequired('u wat'),
                                                  Email('Please enter a valid Email address.')])
    update = SubmitField('Update address')
    resend = SubmitField('Send verification mail again')


@blueprint.route('/settings/email', methods=['GET', 'POST'])
@login_required
def email_pane():

    form = EmailUpdateForm(request.form)

    if request.method == 'POST':
        if form.validate():
            if form.update.data:
                if current_user.mail == form.mail.data and current_user.mail_verified:
                    flash("This address is already verified with your account.")
                    return redirect(url_for('settings.email_pane'))

                current_user.mail = form.mail.data
                current_user.mail_verified = False
                current_user.save()
                send_verification_mail()
                flash('A verification email has been sent.')
            elif form.resend.data:
                send_verification_mail()
                flash('A verification email has been sent.')
        else:
            return render_template('settings_email.html', form=form)

        return redirect(url_for('settings.email_pane'))

    form.mail.data = current_user.mail if not form.mail.data else form.mail.data
    return render_template('settings_email.html', settings_panels_structure=settings_panels_structure, form=form, title="Settings - Account - Email")


DATA_VER = 3


@blueprint.route('/settings/email/verify/<string:data>')
def verify_email(data):
    payload = serializer.loads(data, salt="MailVerification")

    if len(payload) != 4 or payload[0] != DATA_VER:
        abort(404)

    if (datetime.datetime.utcnow() - datetime.datetime.fromtimestamp(payload[3])).seconds > 3600:
        abort(404)

    user = User.objects(name=payload[1]).first()
    if user is None:
        abort(404)

    if user.mail_verified:
        abort(404)

    if user.mail != payload[2]:
        abort(404)

    user.mail_verified = True
    user.save()
    return 'Success'


def send_verification_mail():
    link = url_for('settings.verify_email',
                   data=serializer.dumps([DATA_VER ,current_user.name, current_user.mail, time.mktime(datetime.datetime.utcnow().timetuple())], salt="MailVerification"),
                   _external=True)
    message = Message('Junction.at Email Verification',
                      sender="noreply@junction.at",
                      recipients=[current_user.mail],
                      body="Click here to confirm this mail with %s on Junction.at: %s" % (current_user.name, link))
    mail.send(message)

add_settings_pane(lambda: url_for('settings.email_pane'), "Account", "Email")
