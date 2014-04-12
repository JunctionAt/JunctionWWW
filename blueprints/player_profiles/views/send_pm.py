__author__ = 'HansiHE'

from flask import render_template, redirect, abort, request, flash
from flask_wtf import Form
from wtforms import TextAreaField, SubmitField
from wtforms.validators import Length, Required

from .. import blueprint
from blueprints.auth import User, current_user, login_required
from models.notification_model import PMNotification


class ComposePMForm(Form):
    text = TextAreaField("Profile text", validators=[
        Required(message="Some text is required."),
        Length(min=3, max=5000, message="The message must be between 3 and 5000 characters.")])
    submit = SubmitField("Submit")


@blueprint.route('/p/<string:name>/pm/', methods=['GET', 'POST'])
@login_required
def send_pm(name):
    user = User.objects(name=name).first()
    if user is None:
        abort(404)

    form = ComposePMForm(request.form)

    if request.method == 'POST':
        if not form.validate():
            return render_template('profile_send_pm.html', user=user, form=form)

        notification = PMNotification(receiver=user.name, sender=current_user.name,
                                      source="Website", message=form.text.data)
        #    receiver=user.to_dbref(), sender_type=1, sender_user=current_user.to_dbref(),
        #    preview="PM from %s" % current_user.name, deletable=True, type="pm", module="pm", render_type=1,
        #    data={'text': form.text.data})
        notification.save()

        flash('The PM has been successfully sent.', category='success')

        return redirect(user.get_profile_url())

    return render_template('profile_send_pm.html', user=user, form=form, title="Send PM - " + user.name + " - Profile")
