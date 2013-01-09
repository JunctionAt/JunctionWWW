__author__ = 'HansiHE'

from .. import bans
from flask import render_template, abort, redirect, url_for, request
from flask_login import current_user
from wtforms import Form, TextAreaField
from wtforms.validators import Required, Length
from blueprints.bans.ban_model import Ban
from blueprints.bans.appeal_model import Appeal, AppealReply
from blueprints.auth import login_required
import math

"""
This file should contain everything related to viewing, editing and posting to appeals.
"""

class AppealReplyForm(Form):
    text = TextAreaField()

@bans.route('/a/appeal/view/<int:uid>', methods=("GET", "POST"))
def view_appeal(uid):

    reply_form = AppealReplyForm(request.form)

    ban = Ban.objects(uid=uid).first()
    if ban is None:
        abort(404)

    appeal = ban.appeal
    if appeal is None:
        #TODO: Should redirect to the ban
        abort(404)

    #if request.method == "GET":
    #    pass

    if request.method == "POST" and current_user.is_authenticated():
        reply = AppealReply(creator=current_user.to_dbref(), text=reply_form.text.data)
        appeal.replies.append(reply)
        appeal.save()

    print appeal.replies
    replies = sorted(appeal.replies, lambda key, reply: int(reply.created.strftime("%s")))
    return render_template(
        'view_appeal.html',
        reply_form=reply_form,
        ban=ban,
        replies=replies
    )

    #abort(404)


class NewAppealForm(Form):
    text = TextAreaField('Appeal Text', [ Required(), Length(min=8) ])

@bans.route('/a/appeal/new/<int:uid>', methods=("GET", "POST"))
@login_required
def post_new_appeal(uid):

    form = NewAppealForm(request.form)

    ban = Ban.objects(uid=uid, active=True).first()

    if ban is None:
        abort(404)

    if (hasattr(ban, 'appeal') and ban.appeal != None and ban.username != current_user.name):
        abort(404)

    if request.method == 'GET':
        return render_template(
            'new_appeal.html',
            form=form
        )

    if request.method == 'POST':
        appeal = Appeal(ban=ban)
        reply = AppealReply(creator=current_user.to_dbref(), text=form.text.data)
        appeal.replies.append(reply)
        appeal.save()
        ban.appeal = appeal.to_dbref()
        ban.save()

        return 'ye'
