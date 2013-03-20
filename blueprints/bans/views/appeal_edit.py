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

class ReplyEditForm(Form):
    text = TextAreaField('Text', validators=[ Required(), Length(min=1, message="Please don't leave the textbox empty.") ])
    submit = SubmitField('Submit')
    #delete = SubmitField('Delete Post')

@bans.route('/a/appeal/edit/<int:uid>', methods=["GET", "POST"])
@login_required
def edit_reply(uid):

    if not current_user.has_permission("bans.appeal.edit"):
        abort(403)

    form = ReplyEditForm(request.form)

    reply = AppealReply.objects(uid=uid).first()
    if reply is None:
        abort(404)

    if request.method == "POST":
        if form.submit.data:
            form.validate()
            reply.edited = datetime.datetime.utcnow()
            print form.text.data
            reply.editor = current_user.to_dbref()
            reply.edits.append(AppealEdit(text=form.text.data, user=current_user.to_dbref()))
            reply.text = form.text.data
            reply.save()
            return redirect(url_for('bans.view_appeal', uid=reply.appeal.ban.uid))
            #elif form.delete.data:
            #    appeal = reply.appeal
            #    appeal.replies.remove(reply.to_dbref())
            #    appeal.save()
            #    reply.remove()

    if request.method == "GET":
        form.text.data = reply.text
        return render_template(
            'edit_appeal_reply.html',
            form=form
        )