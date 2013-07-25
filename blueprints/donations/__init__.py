__author__ = 'HansiHE'

from flask import Blueprint, render_template, send_file, abort, redirect, request
from itsdangerous import URLSafeSerializer
from blueprints.auth import current_user, login_required
from donation_model import Transaction, DonationTransaction
from blueprints.base import cache
from wtforms import Form, DateField

blueprint = Blueprint('donations', __name__,
                         template_folder='templates')

# Used for signing usernames when we pass them to paypal.
username_signer = URLSafeSerializer("yKkBdpiHAiAInsbX92bSMW0MKErI1jLRso39yTF7", salt="PaypalDonateUsername")

import ipn

@blueprint.route('/donate')
def donate():
    funds_target = 50
    donations = DonationTransaction.objects(valid=True)
    return render_template(
        'donate_newer.html',
        funds_target=funds_target,
        funds_current=donations.sum('amount'),
        total_fees=donations.sum('fee'),
        total_donations=DonationTransaction.objects(valid=True, gross__gt=0).sum('gross'),
        num_donations=len(donations),
        top_donations=donations.order_by('-amount').limit(5).only('gross', 'fee', 'username', 'valid'),
        signed_user=username_signer.dumps(current_user.name) if current_user.is_authenticated() else None
        )

@cache.memoize(make_name=lambda: "donation_stats_data")
def get_donations_stats_data():
    pass


class RenewDateForm(Form):
    date = DateField('Renew Date', format='%Y-%m-%d')

@blueprint.route('/donate/set_renew_date')
@login_required
def set_renew_date():
    if not current_user.has_permission('financial.set_renew'):
        return redirect('/')

    form = RenewDateForm(request.form)

    if request.method == "POST" and form.validate():
        return 'ya'

    return render_template('set_renew_date.html', form=form)