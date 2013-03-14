__author__ = 'HansiHE'

from . import blueprint
from flask import request
from werkzeug.datastructures import ImmutableOrderedMultiDict
import requests

@blueprint.route('/donate/ipn_callback', methods=['POST'])
def ipn_listener():
    arg = ''
    #: We use an ImmutableOrderedMultiDict item because it retains the order.
    request.parameter_storage_class = ImmutableOrderedMultiDict
    values = request.form
    for x, y in values.iteritems():
        if len(arg) is not 0:
            arg += "&"
        arg += "{x}={y}".format(x=x,y=y)
    arg += ""

    validate_url = 'https://www.paypal.com/cgi-bin/webscr?cmd=_notify-validate&'

    print 'Validating IPN using {url}'.format(url=validate_url)

    r = requests.get(validate_url, data=arg, headers={
        "Content-Type": "application/x-www-form-urlencoded",
        "Content-Length": str(len(arg)),
        "Host": "www.paypal.com",
        "Connection": "Close"
    })

    if r.text == 'VERIFIED':
        print "PayPal transaction was verified successfully."
        # Do something with the verified transaction details.
        payer_email =  request.form.get('payer_email')
        print "Pulled {email} from transaction".format(email=payer_email)
    else:
        print 'Paypal IPN string {arg} did not validate'.format(arg=arg)

    print r.status_code

    return r.text