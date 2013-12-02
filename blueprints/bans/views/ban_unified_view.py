__author__ = 'HansiHE'

from flask import abort, render_template, request, redirect, url_for
from .. import bans
from ..ban_model import Ban, Note, AppealReply, AppealEdit
from blueprints.alts.alts_model import PlayerIpsModel
from .. import process_ban
from blueprints.auth import login_required, current_user
from flask_wtf import Form
from wtforms import TextAreaField, SubmitField
from wtforms.validators import Required, Length
import datetime


class AppealReplyForm(Form):
    text = TextAreaField('Text', validators=[
        Required(message="Some content is required."),
        Length(min=1, max=5000, message="Content must be between 1 and 5000 characters long.")])
    submit = SubmitField('Post')


class BanTextEditForm(Form):
    text = TextAreaField('Text', validators=[
        Required(message="Some content is required."),
        Length(min=1, max=5000, message="Content must be between 1 and 5000 characters long.")])
    submit = SubmitField('Edit')


@bans.route('/a/ban/<int:ban_uid>', methods=['GET'])
def view_ban(ban_uid):

    ban = Ban.objects(uid=ban_uid).first()
    if ban is None:
        abort(404)

    process_ban(ban)

    appeal = ban.appeal

    #if appeal:
    #    if appeal.state == 1:
    #        if appeal.unlock_time and appeal.unlock_time < datetime.datetime.utcnow():
    #            appeal.state = 0
    #            appeal.save()

    replies = AppealReply.objects(ban=ban).order_by('+created')
    notes = Note.objects(username=ban.username, active=True)

    can_post = current_user.has_permission("bans.appeal.manage") or (current_user.is_authenticated() and current_user.name.lower() == ban.username.lower())

    alts = None
    if current_user.has_permission("bans.appeal.alts"):
        user_ips = PlayerIpsModel.objects(username__iexact=ban.username).first()
        if user_ips:
            alts = PlayerIpsModel.objects(ips__in=user_ips.ips, username__ne=ban.username)

    return render_template('bans_unified_view.html', ban_id=ban_uid, ban_object=ban, appeal_object=appeal, notes=notes,
                           reply_form=AppealReplyForm(), edit_form=BanTextEditForm(), replies=replies,
                           can_post=can_post, alts=alts)

@bans.route('/a/ban/<int:ban_uid>/reply', methods=["POST"])
@login_required
def post_ban_reply(ban_uid):
    reply_form = AppealReplyForm(request.form)

    ban = Ban.objects(uid=ban_uid).first()
    if ban is None:
        abort(404)

    if not (current_user.has_permission("bans.appeal.manage") or (current_user.is_authenticated() and current_user.name.lower() == ban.username.lower())):
        abort(403)

    appeal = ban.appeal

    if request.method == "POST" and reply_form.validate():
        last_reply = AppealReply.objects(ban=ban).order_by('-created').first()

        if last_reply and last_reply.creator.name == current_user.name:
            last_reply.text += "\n- - -\n" + reply_form.text.data
            last_reply.edits.append(AppealEdit(text=last_reply.text, user=current_user.to_dbref()))
            last_reply.save()
            return redirect(url_for('bans.view_ban', ban_uid=ban_uid))
        else:
            reply = AppealReply(creator=current_user.to_dbref(), text=reply_form.text.data, ban=ban)
            reply.edits.append(AppealEdit(text=reply_form.text.data, user=current_user.to_dbref()))
            reply.save()
            appeal.replies.append(reply)
            appeal.last = datetime.datetime.utcnow()
            ban.save()
            return redirect(url_for('bans.view_ban', ban_uid=ban_uid))