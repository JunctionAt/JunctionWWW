__author__ = 'HansiHE'

from .. import bans
from flask import render_template, abort, redirect, url_for, request, flash
from flask_login import current_user
from wtforms import Form, TextAreaField, SelectField, SubmitField, TextField, BooleanField, DateField
from wtforms.validators import Required, Length
from blueprints.bans.ban_model import Ban
from blueprints.bans.appeal_model import Appeal, AppealReply, AppealEdit
from blueprints.auth import login_required
import math
import datetime

class RequiredIf(Required):
    # a validator which makes a field required if
    # another field is set and has a truthy value

    def __init__(self, other_field_name, *args, **kwargs):
        self.other_field_name = other_field_name
        super(RequiredIf, self).__init__(*args, **kwargs)

    def __call__(self, form, field):
        other_field = form._fields.get(self.other_field_name)
        if other_field is None:
            raise Exception('no field named "%s" in form' % self.other_field_name)
        if bool(other_field.data):
            super(RequiredIf, self).__call__(form, field)

class HideReplyForm(Form):
    hide = BooleanField('Hide/show the reply', validators=[Required])

@bans.route('/a/appeal/action/hide_reply/<int:uid>/', methods=["POST"])
@login_required
def hide_reply(uid):

    if not current_user.has_permission("bans.appeal.hide"):
        abort(403)

    reply = AppealReply.objects(uid=uid).first()
    if reply is None:
        abort(404)

    hide_form = HideReplyForm(request.form)

    reply.hidden = hide_form.hide.data
    reply.save()

    return 'SUCCESS'

class UnbanDateForm(Form):
    remove = SubmitField('Remove the set date')
    set = SubmitField('Set the unban date')
    date = DateField('The date you want the ban removed', validators=[RequiredIf('set')], format='%m/%d/%Y')

@bans.route('/a/appeal/action/set_unban_date/<int:uid>/')
@login_required
def set_unban_date(uid):

    if not current_user.has_permission("bans.appeal.unban"):
        abort(403)

    ban = Ban.objects(uid=uid).first()
    if ban is None:
        abort(404)

    unban_date_form = UnbanDateForm(request.form)

    if unban_date_form.remove.data:
        ban.removal_time = None
        ban.remover = None
    elif unban_date_form.set.data:
        ban.removal_time = unban_date_form.date.data
        ban.remover = current_user.name

    ban.save()

    return 'SUCCESS'

@bans.route('/a/appeal/action/remove_ban_id/<int:uid>/')
@login_required
def unban_ban_id(uid):

    if not current_user.has_permission("bans.appeal.unban"):
        abort(403)

    ban = Ban.objects(uid=uid).first()
    if ban is None:
        abort(404)

    ban.active = False
    ban.remover = current_user.name

    ban.save()

    return 'SUCCESS'

