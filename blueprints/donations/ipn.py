__author__ = 'HansiHE'

from . import blueprint
from flask import request, current_app
from werkzeug.datastructures import ImmutableOrderedMultiDict
import requests
from donation_model import Transaction, TransactionStatus, TransactionLog
from . import username_signer
from itsdangerous import BadData, BadPayload, BadSignature
from blueprints.base import cache

is_debug = current_app.config['PAYPAL_IPN_DEBUG_MODE']

@blueprint.route('/donate/ipn_callback', methods=['POST'])
def ipn_listener():
    #arg = ''
    values = request.form.to_dict()
    #for x, y in values.iteritems():
    #    if len(arg) is not 0:
    #        arg += "&"
    #    arg += "%s=%s"% (x, y,)
    #arg += ""

    values['cmd'] = "_notify-validate"

    validate_url = "https://www.paypal.com/cgi-bin/webscr" if not is_debug else "https://www.sandbox.paypal.com/cgi-bin/webscr"

    print values

    print 'Validating IPN using %s' % validate_url

    r = requests.post(validate_url, data=values, headers={
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "www.paypal.com",
        "Connection": "Close"
    })

    print r.text
    if r.text == 'VERIFIED':
        print "PayPal transaction was verified successfully."
        if is_debug:
            print values
        else:
            process_transaction(values)
        payer_email = request.form.get('payer_email')
        print "Pulled {email} from transaction".format(email=payer_email)
    else:
        pass
        #print 'Paypal IPN string {arg} did not validate'.format(arg=arg)

    print r.status_code

    return r.text


def process_transaction(data):

    # Get the username
    if not data.get("custom", None) or data.get("custom", None) == "None":
        username = None
    else:
        try:
            username = username_signer.loads(data["custom"])
        except (BadPayload, BadData, BadSignature):
            username = None

    TransactionLog(data=data, username=username).save()

    txn_id = data.get("parent_txn_id") or data.get("txn_id")

    # Check if the transaction already exists in db.
    transaction = Transaction.objects(transaction_id=txn_id).first()
    if transaction:
        pass
    else:
        transaction = Transaction()

        transaction.username = username
        transaction.email = data["payer_email"]

        transaction.gross = float(data.get("mc_gross", 0))
        transaction.fee = float(data.get("mc_fee", 0))
        transaction.amount = transaction.gross - transaction.fee
        transaction.payment_type = data.get("payment_type", "")
        transaction.transaction_id = txn_id

    transaction_status = TransactionStatus()
    transaction_status.status = data["payment_status"]
    transaction_status.reason = data.get("pending_reason", None) or data.get("reason_code", None)
    transaction_status.valid = validate_transaction(data)
    transaction_status.gross = float(data.get("mc_gross", 0))
    transaction_status.fee = float(data.get("mc_fee", 0))
    transaction_status.complete_data = data
    transaction.payment_status_events.append(transaction_status)

    transaction.valid = validate_transaction(data)

    transaction.save()

    cache.delete_memoized('donation_stats_data')


def validate_transaction(data):
    return data["payment_status"] in ["Canceled_Reversal", "Completed", "Pending", "Processed"]