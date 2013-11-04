__author__ = 'HansiHE'

from .. import bans
from flask import render_template, abort, redirect, url_for, request, flash
from flask_login import current_user
from flask_wtf import Form
from wtforms import TextAreaField, SelectField, SubmitField, TextField
from wtforms.validators import Required, Length
from blueprints.bans.ban_model import Ban
from blueprints.bans.appeal_model import Appeal, AppealReply, AppealEdit
from blueprints.auth import login_required
import math
import datetime

class ReplyEditForm(Form):
    text = TextAreaField('Text', validators=[
        Required(message="Some content is required."),
        Length(min=1, max=5000, message="Content must be between 1 and 5000 characters long.")])
    submit = SubmitField('Submit')
    #delete = SubmitField('Delete Post')

@bans.route('/a/appeal/edit/<int:uid>', methods=["GET", "POST"])
@login_required
def edit_reply(uid):

    form = ReplyEditForm(request.form)

    reply = AppealReply.objects(uid=uid).first()
    if reply is None:
        abort(404)

    ban = Ban.objects(uid=reply.appeal.ban.uid).first()
    if ban is None:
        abort(404)

    appeal = reply.appeal
    if appeal is None:
        abort(404)

    if not current_user.has_permission("bans.appeal.edit") or (current_user.name.lower() == ban.username.lower() and appeal.state==0):
        abort(403)

    if request.method == "POST" and form.validate():
        reply.edits.append(AppealEdit(text=form.text.data, user=current_user.to_dbref(), time=datetime.datetime.utcnow()))
        reply.edited = datetime.datetime.utcnow()
        reply.editor = current_user.to_dbref()
        reply.text = form.text.data
        reply.save()
        return redirect(url_for('bans.view_appeal', uid=ban.uid))

    form.text.data = reply.text
    return render_template('edit_appeal_reply.html', form=form, ban=ban, title='Anathema - Appeals - Appeal #' + str(ban.uid) + ' - Edit Reply')
