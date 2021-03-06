from mongoengine import *
from datetime import datetime

from models.user_model import User


class TransactionLog(Document):

    username = StringField()
    date = DateTimeField(required=True, default=datetime.utcnow)
    data = DictField()


class DonationTransactionStatus(EmbeddedDocument):

    date = DateTimeField(required=True, default=datetime.utcnow)
    status = StringField(required=True)  # = payment_status
    reason = StringField()  # = pending_reason if exists or reason_code if exists
    valid = BooleanField(required=True)

    gross = FloatField(default=0)
    fee = FloatField(default=0)

    complete_data = DictField()


class Transaction(Document):

    amount = FloatField(required=True)  # = the actual calculated amount

    created = DateTimeField(required=True, default=datetime.utcnow)

    # https://developer.paypal.com/webapps/developer/docs/classic/ipn/integration-guide/IPNandPDTVariables/#id091EB04C0HS__id0913D0E0UQU
    # Canceled_Reversal: valid=true
    # Completed: valid=true
    # Created: valid=false
    # Denied: valid=false
    # Expired: valid=false
    # Failed: valid=false
    # Pending: valid=true, reason=pending_reason
    # Refunded: valid=false
    # Reversed: valid=false, reason=ReasonCode
    # Processed: valid=true
    # Voided: valid=false

    meta = {
        'collection': 'financial_transactions',
        'allow_inheritance': True,
        'indexes': [
            'amount'
        ]
    }


class DonationTransaction(Transaction):

    username = StringField()
    email = StringField()

    gross = FloatField(required=True)  # = the total amount donated
    fee = FloatField(required=True)  # = the amount paypal has robbed us for
    payment_type = StringField()  # Should be either echeck or instant
    transaction_id = StringField()  # = parent_txn_id or txn_id, unique id
    valid = BooleanField()  # Could be used for easy querying, should be set when payment_status is Pending or Completed. Changed to false if shit happens.

    payment_status_events = ListField(EmbeddedDocumentField(DonationTransactionStatus))  # list of states received for this transaction

    type = "donation"

    meta = {
        'allow_inheritance': True,
        'indexes': [
            'username',
        #    'amount',
            {
                'fields': ['transaction_id'],
                'unique': True,
                'sparse': True
            }
        ]
    }


class PaymentTransaction(Transaction):

    note = StringField()
    period_begin = DateTimeField(required=True)
    period_end = DateTimeField(required=True)
    user = ReferenceField(User, dbref=False, required=True)

    type = "payment"