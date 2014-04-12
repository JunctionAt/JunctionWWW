__author__ = 'HansiHE'

from flask_wtf import Form
from wtforms import TextAreaField, DateField, SubmitField, FloatField
from flask import request, render_template, redirect, url_for, abort

from .. import blueprint
from blueprints.auth import login_required, current_user
from models.donation_model import PaymentTransaction


class PaymentAddForm(Form):

    amount = FloatField("Amount (Negative if subtract)")
    note = TextAreaField("Note")
    start_date = DateField("Start")
    end_date = DateField("End")
    submit = SubmitField("Submit")


@blueprint.route('/donate/add_payment/', methods=['POST', 'GET'])
@login_required
def add_payment():
    if not current_user.has_permission('financial.payments'):
        abort(403)

    form = PaymentAddForm(request.form)

    if request.method == "POST":

        payment = PaymentTransaction()

        payment.amount = form.amount.data
        payment.period_begin = form.start_date.data
        payment.period_end = form.end_date.data
        payment.user = current_user.to_dbref()
        payment.note = form.note.data

        payment.save()

        return redirect(url_for('donations.donate'))

    return render_template("add_payment.html", form=form)