__author__ = 'HansiHE'

from .. import blueprint
from ..donation_model import PaymentTransaction
from flask import render_template


@blueprint.route('/donate/payments')
def payments_view():
    payments = PaymentTransaction.objects().order_by('-period_begin')

    return render_template('payments_view.html', payments=payments)