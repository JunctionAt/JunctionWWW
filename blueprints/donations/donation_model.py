__author__ = 'HansiHE'

from mongoengine import *
from datetime import datetime

class Donation(Document):

    username = StringField()
    amount = FloatField()
    time = DateTimeField(required=True, default=datetime.utcnow)
    transaction_id = StringField()

    meta = {
        'collection': 'financial_transactions',
        'indexed': [ 'username', 'amount' ]
    }