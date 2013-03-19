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

"""
This file should contain everything related to viewing, editing and posting to appeals.
"""

class AppealReplyForm(Form):
    text = TextAreaField('Text')
    submit = SubmitField('Submit')

class AppealAdminForm(Form):
    unban = SubmitField('Unban Now')
    lock_time = SelectField('Lock length', choices=[
        ('-1', 'Forever'), ('1','(1) One day'),
        ('2', '(2) Two days'), ('3', '(3) Three days'),
        ('4', '(4) Four days'), ('5', '(5) Five days'),
        ('6', '(6) Six days'), ('7', '(1) One week'),
        ('14', '(2) Two weeks'), ('21', '(3) Three weeks'),
        ('28', '(1) One month'), ('56', '(2) Two months'),
        ('84', '(3) Three months'), ('112', '(4) Four months'),

    ])
    lock = SubmitField('Lock Appeal')
    unlock = SubmitField('Unlock Appeal')

    unban_time = TextField('Unban date:')
    unban_time_submit = SubmitField('Set')
    unban_time_remove = SubmitField('Remove')

    unlock_time = TextField('Unlock date:')
    unlock_time_submit = SubmitField('Set')
    unlock_time_remove = SubmitField('Remove')

@bans.route('/a/appeal/view/<int:uid>', methods=['GET'])
def view_appeal(uid):

    reply_form = AppealReplyForm(request.form)
    admin_form = AppealAdminForm(request.form)

    ban = Ban.objects(uid=uid).first()
    if ban is None:
        abort(404)

    appeal = ban.appeal
    if appeal is None:
        #TODO: Should redirect to the ban
        abort(404)

#    if request.method == "POST" and current_user.is_authenticated():
#        if (current_user.has_permission("bans.appeal.manage") or (current_user.name.lower() == ban.username.lower() and appeal.state==0)) and reply_form.submit.data:
#            reply = AppealReply(creator=current_user.to_dbref(), text=reply_form.text.data, appeal=appeal)
#            reply.edits.append(AppealEdit(text=reply_form.text.data, user=current_user.to_dbref()))
#            reply.save()
#            appeal.replies.append(reply)
#            appeal.last = datetime.datetime.utcnow()
#            appeal.save()
#        elif current_user.has_permission("bans.appeal.manage"):
#            if admin_form.unban.data:
#                ban.active=False
#                ban.save()
#            elif admin_form.lock.data:
#                time = int(admin_form.lock_time.data)
#                if time == -1:
#                    appeal.state = 2
#                    appeal.save()
#                else:
#                    appeal.state = 1
#                    delta = datetime.timedelta(days=time)
#                    appeal.locked_until = datetime.datetime.utcnow() + delta
#                    appeal.save()
#            elif admin_form.unlock.data:
#                appeal.state = 0
#                appeal.save()

    if appeal.state == 1:
        if appeal.locked_until < datetime.datetime.utcnow():
            appeal.state = 0
            del(appeal.locked_until)
            appeal.save()

    replies = sorted(appeal.replies, lambda key, reply: int(reply.created.strftime("%s")))
    return render_template(
        'view_appeal.html',
        reply_form=reply_form,
        admin_form=admin_form,
        ban=ban,
        replies=replies,
        locked=appeal.state!=0,
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

@bans.route('/a/appeal/action/manage/<int:uid>', methods=['POST'])
@login_required
def post_manage_appeal(uid):

    admin_form = AppealAdminForm(request.form)

    ban = Ban.objects(uid=uid).first()
    if ban is None:
        abort(404)

    appeal = ban.appeal
    if appeal is None:
        abort(404)

    if current_user.has_permission("bans.appeal.manage"):
        if admin_form.unban.data:
            ban.active=False
            ban.save()
        elif admin_form.lock.data:
            time = int(admin_form.lock_time.data)
            if time == -1:
                appeal.state = 2
                appeal.save()
            else:
                appeal.state = 1
                delta = datetime.timedelta(days=time)
                appeal.locked_until = datetime.datetime.utcnow() + delta
                appeal.save()
        elif admin_form.unlock.data:
            appeal.state = 0
            appeal.save()
    else:
        flash('Unauthorized')

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

    if (hasattr(ban, 'appeal') and ban.appeal != None and ban.username != current_user.name):
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

@bans.route('/a/appeal/action/hide_reply/<int:uid>', methods=["GET"])
@login_required
def hide_reply(uid):

    if not current_user.has_permission("bans.appeal.hide"):
        abort(403)

    reply = AppealReply.objects(uid=uid).first()
    if reply is None:
        abort(404)

    reply.hidden = True
    reply.save()

    return redirect(url_for('bans.view_appeal', uid=reply.appeal.ban.uid))

@bans.route('/a/appeal/action/unhide_reply/<int:uid>', methods=["GET"])
@login_required
def unhide_reply(uid):

    if not current_user.has_permission("bans.appeal.hide"):
        abort(403)

    reply = AppealReply.objects(uid=uid).first()
    if reply is None:
        abort(404)

    reply.hidden = False
    reply.save()

    return redirect(url_for('bans.view_appeal', uid=reply.appeal.ban.uid))