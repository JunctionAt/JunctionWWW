from flask import abort, render_template, request, redirect, url_for
from flask_wtf import Form
from wtforms import TextAreaField, SubmitField
from wtforms.validators import InputRequired, Length
import datetime

from .. import bans
from models.ban_model import Ban, Note, AppealReply, AppealEdit, BanNotification
from models.alts_model import PlayerIpsModel
from blueprints.auth import login_required, current_user
from .ban_editing import BanReasonEditForm, AppealReplyTextEditForm
from .ban_manage import BanUnbanTimeForm, AppealUnlockTimeForm
import js_state_manager


class AppealReplyForm(Form):
    text = TextAreaField('Text', validators=[
        InputRequired(message="Some content is required."),
        Length(min=1, max=5000, message="Content must be between 1 and 5000 characters long.")])
    submit = SubmitField('Post')


def user_can_post(user, ban):
    return user.can("reply to ban appeals") or \
        (user.is_authenticated() and user.is_player(ban.target) and ban.appeal.state == 'open')


@bans.route('/a/ban/<int:ban_uid>', methods=['GET'])
def view_ban(ban_uid):

    ban = Ban.objects(uid=ban_uid).first()
    if ban is None:
        abort(404)

    appeal = ban.appeal

    if ban.appeal.state == 'closed_time':
        if ban.appeal.unlock_time and ban.appeal.unlock_time < datetime.datetime.utcnow():
            ban.appeal.state = 'open'
            ban.save()

    replies = AppealReply.objects(ban=ban).order_by('+created')
    notes = Note.objects(target=ban.target, active=True)

    can_post = user_can_post(current_user, ban)

    alts = []
    if current_user.can("view alts"):
        user_ips = PlayerIpsModel.objects(player=ban.target).first()
        if user_ips:
            alts = PlayerIpsModel.objects(ips__in=user_ips.ips, player__ne=ban.target)

    unlock_time_form = AppealUnlockTimeForm()
    if appeal.unlock_time:
        unlock_time_form.date.data = appeal.unlock_time
    unban_time_form = BanUnbanTimeForm()
    if ban.removed_time:
        unban_time_form.date.data = ban.removed_time

    js_state_manager.get_manager().update({
        'ban': {
            'watching': current_user in ban.watching,
            'id': ban.uid
        }
    })

    return render_template('bans_unified_view.html', ban_id=ban_uid, ban_object=ban, appeal_object=appeal, notes=notes,
                           reply_form=AppealReplyForm(), edit_form=BanReasonEditForm(), reply_edit_form=AppealReplyTextEditForm(),
                           unlock_time_form=unlock_time_form, unban_time_form=unban_time_form, replies=replies,
                           can_post=can_post, alts=alts)

@bans.route('/a/ban/<int:ban_uid>/reply', methods=["POST"])
@login_required
def post_ban_reply(ban_uid):
    reply_form = AppealReplyForm(request.form)

    ban = Ban.objects(uid=ban_uid).first()
    if ban is None:
        abort(404)

    if not user_can_post(current_user, ban):
        abort(403)

    appeal = ban.appeal

    if request.method == "POST" and reply_form.validate():
        last_reply = AppealReply.objects(ban=ban).order_by('-created').first()

        # If the user just posted a reply, treat this as an edit of his previous post.
        if last_reply and last_reply.creator.name == current_user.name:
            last_reply.text += "\n- - -\n" + reply_form.text.data
            last_reply.edits.append(AppealEdit(text=last_reply.text,
                                               user=current_user.to_dbref()))
            last_reply.save()
            return redirect(url_for('bans.view_ban', ban_uid=ban_uid))

        else:
            reply = AppealReply(creator=current_user.to_dbref(), text=reply_form.text.data, ban=ban)
            reply.edits.append(AppealEdit(text=reply_form.text.data, user=current_user.to_dbref()))
            reply.save()
            appeal.replies.append(reply)
            appeal.last = datetime.datetime.utcnow()
            ban.save()
            
            BanNotification.send_notifications(ban, action="reply")
            
            return redirect(url_for('bans.view_ban', ban_uid=ban_uid))
