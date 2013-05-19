__author__ = 'HansiHE'

from .. import bans
from flask import render_template, abort, redirect, url_for, request, flash
from flask_login import current_user
from wtforms import Form, TextAreaField, SelectField, SubmitField, TextField
from wtforms.validators import Required, Length
from blueprints.bans.ban_model import Ban
from blueprints.bans.appeal_model import Appeal, AppealReply, AppealEdit
from blueprints.auth import login_required
import math
import datetime
from .. import process_ban

"""
This file should contain everything related to viewing, editing and posting to appeals.
"""


class AppealReplyForm(Form):
    text = TextAreaField('Text')
    submit = SubmitField('Submit')


@bans.route('/a/appeal/view/<int:uid>', methods=['GET'])
def view_appeal(uid):

    reply_form = AppealReplyForm(request.form)

    ban = Ban.objects(uid=uid).first()
    if ban is None:
        abort(404)

    process_ban(ban)

    appeal = ban.appeal
    if appeal is None:
        #TODO: Should redirect to the ban
        abort(404)

    if appeal.state == 1:
        if appeal.unlock_time and appeal.unlock_time < datetime.datetime.utcnow():
            appeal.state = 0
            appeal.save()

    for reply in appeal.replies:
        print reply

    replies = sorted(appeal.replies, lambda key, reply: int(reply.created.strftime("%s")))

    return render_template(
        'view_appeal.html',
        reply_form=reply_form,
#        admin_form=admin_form,
        ban=ban,
        replies=replies,
        appeal=appeal,
        locked=appeal.state != 0,
        is_mod = current_user.has_permission("bans.appeal.manage")
    )

    #abort(404)


@bans.route('/a/appeal/action/reply/<int:uid>', methods=['POST'])
@login_required
def post_appeal_reply(uid):

    reply_form = AppealReplyForm(request.form)

    ban = Ban.objects(uid=uid).first()
    if ban is None:
        abort(404)

    appeal = ban.appeal
    if appeal is None:
        abort(404)

    if (current_user.has_permission("bans.appeal.manage") or (current_user.name.lower() == ban.username.lower() and appeal.state==0)) and reply_form.submit.data:
        reply = AppealReply(creator=current_user.to_dbref(), text=reply_form.text.data, appeal=appeal)
        reply.edits.append(AppealEdit(text=reply_form.text.data, user=current_user.to_dbref()))
        reply.save()
        appeal.replies.append(reply)
        appeal.last = datetime.datetime.utcnow()
        appeal.save()

    return redirect(url_for('bans.view_appeal', uid=uid))


class NewAppealForm(Form):
    text = TextAreaField('Appeal Text', [ Required(), Length(min=8) ])


@bans.route('/a/appeal/new/<int:uid>', methods=("GET", "POST"))
@login_required
def post_new_appeal(uid):

    form = NewAppealForm(request.form)

    ban = Ban.objects(uid=uid, active=True).first()

    if ban is None:
        abort(404)

    if hasattr(ban, 'appeal') and ban.appeal is not None and ban.username != current_user.name:
        abort(404)

    if request.method == 'GET':
        return render_template(
            'new_appeal.html',
            form=form
        )

    if request.method == 'POST':
        appeal = Appeal(ban=ban)
        appeal.save()
        reply = AppealReply(creator=current_user.to_dbref(), text=form.text.data, appeal=appeal)
        reply.edits.append(AppealEdit(text=form.text.data, user=current_user.to_dbref()))
        reply.save()
        appeal.replies.append(reply)
        appeal.save()
        ban.appeal = appeal.to_dbref()
        ban.save()

        return redirect(url_for('bans.view_appeal', uid=ban.uid))