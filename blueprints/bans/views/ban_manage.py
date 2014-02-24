__author__ = 'williammck'

from flask import abort, request, redirect, url_for, flash
from .. import bans
from ..ban_model import Ban
from blueprints.auth import login_required, current_user
from flask_wtf import Form
from wtforms import DateField, SubmitField
from wtforms.validators import Required
import datetime

class AppealUnlockTimeForm(Form):
    date = DateField('Appeal Unlock Date', validators=[
        Required(message="A date is required.")])
    submit = SubmitField('Set')

class BanUnbanTimeForm(Form):
    date = DateField('Unban Date', validators=[
        Required(message="A date is required.")])
    submit = SubmitField('Set')

@bans.route('/a/ban/<int:ban_uid>/unban', methods=["GET", "POST"])
@login_required
def unban(ban_uid):
    ban = Ban.objects(uid=ban_uid).first()
    if ban is None:
        abort(404)

    if not current_user.has_permission("bans.appeal.manage"):
        abort(403)

    if not ban.active:
        flash("Ban has already been lifted.", category='alert')
        return redirect(url_for('bans.view_ban', ban_uid=ban_uid))

    if request.method == "POST":
        form = BanUnbanTimeForm(request.form)

        if form.validate():
            ban.removed_time = form.date.data
            ban.removed_by = 'auto_' + current_user.name
            ban.save()
            flash("Ban will be lifted on specified date.", category='success')
            return redirect(url_for('bans.view_ban', ban_uid=ban_uid))
        else:
            flash("Unban date form failed to validate. Make sure you're typing in the right data.", category='alert')
            return redirect(url_for('bans.view_ban', ban_uid=ban_uid))

    ban.active = False
    ban.removed_by = current_user.name
    ban.removed_time = datetime.datetime.utcnow()
    ban.save()
    flash("Ban has been lifted.", category='success')
    return redirect(url_for('bans.view_ban', ban_uid=ban_uid))

@bans.route('/a/ban/<int:ban_uid>/close_appeal', methods=["GET", "POST"])
@login_required
def close_appeal(ban_uid):
    ban = Ban.objects(uid=ban_uid).first()
    if ban is None:
        abort(404)

    if not current_user.has_permission("bans.appeal.manage"):
        abort(403)

    if ban.appeal.state == 'closed_forever':
        flash("Appeal has already been closed.", category='alert')
        return redirect(url_for('bans.view_ban', ban_uid=ban_uid))

    if request.method == "POST":
        form = AppealUnlockTimeForm(request.form)

        if form.validate():
            ban.appeal.unlock_time = form.date.data
            ban.appeal.state = 'closed_time'
            ban.save()
            flash("Appeal closed until specified date.", category='success')
            return redirect(url_for('bans.view_ban', ban_uid=ban_uid))
        else:
            flash("Appeal unlock date form failed to validate. Make sure you're typing in the right data.", category='alert')
            return redirect(url_for('bans.view_ban', ban_uid=ban_uid))

    ban.appeal.state = 'closed_forever'
    ban.save()
    flash("Appeal has been closed.", category='success')
    return redirect(url_for('bans.view_ban', ban_uid=ban_uid))

@bans.route('/a/ban/<int:ban_uid>/open_appeal')
@login_required
def open_appeal(ban_uid):
    ban = Ban.objects(uid=ban_uid).first()
    if ban is None:
        abort(404)

    if not current_user.has_permission("bans.appeal.manage"):
        abort(403)

    if ban.appeal.state == 'open':
        flash("Appeal is already open.", category='alert')
        return redirect(url_for('bans.view_ban', ban_uid=ban_uid))

    ban.appeal.state = 'open'
    ban.save()
    flash("Appeal has been re-opened.", category='success')
    return redirect(url_for('bans.view_ban', ban_uid=ban_uid))
