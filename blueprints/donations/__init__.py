__author__ = 'HansiHE'

from flask import Blueprint, render_template, send_file
from itsdangerous import URLSafeSerializer
from blueprints.auth import current_user
from donation_model import Transaction

blueprint = Blueprint('donations', __name__,
                         template_folder='templates')

# Used for signing usernames when we pass them to paypal.
username_signer = URLSafeSerializer("yKkBdpiHAiAInsbX92bSMW0MKErI1jLRso39yTF7", salt="PaypalDonateUsername")

import ipn

@blueprint.route('/donate')
def donate():
    funds_current = 80
    funds_target = 50
    return render_template(
        'donate_newer.html',
        funds_percentage=round((funds_current/float(funds_target))*100, 1),
        funds_target=funds_target,
        funds_current=Transaction.objects(valid=True).sum('amount'),
        signed_user=username_signer.dumps(current_user.name) if current_user.is_authenticated() else None
        )