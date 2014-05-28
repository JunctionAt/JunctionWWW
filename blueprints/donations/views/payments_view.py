from flask import render_template

from .. import blueprint
from models.donation_model import PaymentTransaction


@blueprint.route('/donate/payments')
def payments_view():
    payments = PaymentTransaction.objects().order_by('+period_begin')

    return render_template('payments_view.html', payments=payments)