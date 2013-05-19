__author__ = 'HansiHE'

from . import blueprint
from flask import request, current_app
from werkzeug.datastructures import ImmutableOrderedMultiDict
import requests

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

    validate_url = "https://www.sandbox.paypal.com/cgi-bin/webscr" if not is_debug else "https://www.sandbox.paypal.com/cgi-bin/webscr"

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
        # Do something with the verified transaction details.
        payer_email = request.form.get('payer_email')
        print "Pulled {email} from transaction".format(email=payer_email)
    else:
        pass
        #print 'Paypal IPN string {arg} did not validate'.format(arg=arg)

    print r.status_code

    return r.text