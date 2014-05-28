__author__ = 'williammck'

from flask import abort, request, redirect, url_for
from flask_wtf import Form
from wtforms import TextAreaField, SubmitField
from wtforms.validators import InputRequired, Length

from .. import bans
from models.ban_model import Ban, AppealEdit, AppealReply
from blueprints.auth import login_required, current_user


class AppealReplyTextEditForm(Form):
    text = TextAreaField('Text', validators=[
        InputRequired(message="Some content is required."),
        Length(min=1, max=5000, message="Content must be between 1 and 5000 characters long.")])
    submit = SubmitField('Edit')


class BanReasonEditForm(Form):
    text = TextAreaField('Ban Reason', validators=[
        InputRequired(message="Some content is required."),
        Length(min=1, max=5000, message="Content must be between 1 and 5000 characters long.")])
    submit = SubmitField('Edit')


@bans.route('/a/ban/<int:ban_uid>/edit', methods=["POST"])
@login_required
def ban_reason_edit(ban_uid):
    edit_form = BanReasonEditForm(request.form)

    if not current_user.has_permission("bans.appeal.manage"):
        abort(403)

    ban = Ban.objects(uid=ban_uid).first()
    if ban is None:
        abort(404)

    if request.method == "POST" and edit_form.validate():
        ban.reason = edit_form.text.data
        ban.save()
        return redirect(url_for('bans.view_ban', ban_uid=ban_uid))


@bans.route('/a/appeals/reply/<string:appeal_reply_id>/edit', methods=["POST"])
@login_required
def appeal_reply_edit(appeal_reply_id):
    edit_form = AppealReplyTextEditForm(request.form)

    appeal_reply = AppealReply.objects(id=appeal_reply_id).first()
    if appeal_reply is None:
        abort(404)

    if not (current_user.has_permission("bans.appeal.manage") or (current_user.is_authenticated() and current_user == appeal_reply.creator)):
        abort(403)

    if request.method == "POST" and edit_form.validate():
        appeal_reply.text = edit_form.text.data
        appeal_reply.edits.append(AppealEdit(text=edit_form.text.data, user=current_user.to_dbref()))
        appeal_reply.save()
        return redirect(url_for('bans.view_ban', ban_uid=appeal_reply.ban.uid))
