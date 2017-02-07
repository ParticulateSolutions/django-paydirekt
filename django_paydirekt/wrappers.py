from __future__ import unicode_literals

import base64
import hashlib
import hmac
import json
import logging
import random
import string
import time
import urllib2
import uuid

from django.conf import settings

from django_paydirekt import settings as django_paydirekt_settings
from django_paydirekt.models import PaydirektCheckout
from django_paydirekt.utils import build_paydirekt_full_uri


class PaydirektWrapper(object):
    interface_version = 'django_paydirekt_v{}'.format(django_paydirekt_settings.DJANGO_PAYDIREKT_VERSION)

    api_url = django_paydirekt_settings.PAYDIREKT_API_URL
    sandbox_url = django_paydirekt_settings.PAYDIREKT_SANDBOX_API_URL
    checkouts_url = django_paydirekt_settings.PAYDIREKT_CHECKOUTS_URL
    token_obtain_url = django_paydirekt_settings.PAYDIREKT_TOKEN_OBTAIN_URL
    transactions_url = django_paydirekt_settings.PAYDIREKT_TRANSACTION_URL

    auth = None

    def __init__(self, auth=None):
        super(PaydirektWrapper, self).__init__()
        if getattr(settings, 'PAYDIREKT', False):
            self.auth = auth
            if django_paydirekt_settings.PAYDIREKT_SANDBOX:
                self.api_url = self.sandbox_url

    def init(self, total_amount, reference_number, payment_type, currency_code='EUR',
             success_url=django_paydirekt_settings.PAYDIREKT_SUCCESS_URL,
             cancellation_url=django_paydirekt_settings.PAYDIREKT_CANCELLATION_URL,
             rejection_url=django_paydirekt_settings.PAYDIREKT_REJECTION_URL,
             notification_url=django_paydirekt_settings.PAYDIREKT_NOTIFICATION_URL,
             overcapture=False,
             email_address=None,
             note=None,
             shipping_amount=None,
             order_amount=None,
             shopping_cart_type=None,
             delivery_information=None,
             delivery_type=None,
             shipping_address=None,
             invoice_reference_number=None,
             reconciliation_reference_number=None,
             minimum_age=None,
             minimum_age_fail_url=None,
             items=None,
             customer_number=None,
             express=False,
             shipping_terms_url=django_paydirekt_settings.PAYDIREKT_SHIPPING_TERMS_URL,
             check_destinations_url=django_paydirekt_settings.PAYDIREKT_NOTIFICATION_URL
        ):

        if not self.auth:
            return False

        if payment_type not in ('DIRECT_SALE', 'ORDER'):
            return False

        success_url = build_paydirekt_full_uri(success_url)
        cancellation_url = build_paydirekt_full_uri(cancellation_url)
        rejection_url = build_paydirekt_full_uri(rejection_url)

        # collecting data for checkout
        checkout_data = {
            'type': payment_type,
            'totalAmount': total_amount,
            'currency': currency_code,
            'merchantOrderReferenceNumber': reference_number,
            'redirectUrlAfterSuccess': success_url,
            'redirectUrlAfterCancellation': cancellation_url,
            'redirectUrlAfterRejection': rejection_url,
            'overcapture': overcapture,
        }

        if express:
            checkout_data.update({'express': True,
                                  'callbackUrlCheckDestinations': build_paydirekt_full_uri(check_destinations_url),
                                  'webUrlShippingTerms': build_paydirekt_full_uri(shipping_terms_url)})
        else:
            if shopping_cart_type != 'ANONYMOUS_DONATION' and shopping_cart_type != 'AUTHORITIES_PAYMENT' and not shipping_address:
                return False
            if shipping_address:
                checkout_data.update({'shippingAddress': shipping_address})
            if delivery_information:
                checkout_data.update({'deliveryInformation': delivery_information})

        notification_url = build_paydirekt_full_uri(notification_url)
        checkout_data.update({'callbackUrlStatusUpdates': notification_url})
        if note:
            checkout_data.update({'note': note})
        if items:
            checkout_data.update({'items': items})
        if shipping_amount:
            checkout_data.update({'shippingAmount': shipping_amount})
        if order_amount:
            checkout_data.update({'orderAmount': order_amount})
        if shopping_cart_type:
            checkout_data.update({'shoppingCartType': shopping_cart_type})
        if shipping_address:
            checkout_data.update({'shippingAddress': shipping_address})
        if delivery_type:
            checkout_data.update({'deliveryType': delivery_type})
        if invoice_reference_number:
            checkout_data.update({'merchantInvoiceReferenceNumber': invoice_reference_number})
        if reconciliation_reference_number:
            checkout_data.update({'merchantReconciliationReferenceNumber': reconciliation_reference_number})
        if minimum_age and minimum_age_fail_url:
            checkout_data.update({'minimumAge': minimum_age,
                                  'redirectUrlAfterAgeVerificationFailure': minimum_age_fail_url})
        if customer_number:
            checkout_data.update({'merchantCustomerNumber': customer_number})
        if email_address:
            sha256_hashed_email_address = hashlib.sha256()
            sha256_hashed_email_address.update(bytes(email_address))
            sha256_hashed_email_address = base64.b64encode(sha256_hashed_email_address.digest())
            checkout_data.update({'sha256hashedEmailAddress': sha256_hashed_email_address})

        checkout_response = self.call_api(url=self.checkouts_url, data=checkout_data)
        if checkout_response and 'totalAmount' in checkout_response and checkout_response['totalAmount'] == float(
                total_amount):
            checkout_id = checkout_response['checkoutId']
            status = checkout_response['status']
            approve_link = checkout_response['_links']['approve']['href']
            link = checkout_response['_links']['self']['href']
            return PaydirektCheckout.objects.create(
                payment_type=payment_type,
                total_amount=total_amount,
                checkout_id=checkout_id,
                status=status,
                approve_link=approve_link,
                link=link
            )
        return False

    def transactions(self,
                     from_datetime=None,
                     to_datetime=None,
                     fields=None,
                     reconciliation_references=None,
                     payment_information_ids=None,
                     merchant_reference_numbers=None,
                     checkout_invoice_numbers=None,
                     capture_invoice_numbers=None):
        if not self.auth:
            return False
        transactions_filters = {}
        if from_datetime:
            transactions_filters.update({'from': from_datetime.isoformat()})
        if from_datetime:
            transactions_filters.update({'to': to_datetime.isoformat()})
        if fields:
            transactions_filters.update({'fields': fields})
        if reconciliation_references:
            transactions_filters.update({'reconciliationReferences': reconciliation_references})
        if payment_information_ids:
            transactions_filters.update({'paymentInformationIds': payment_information_ids})
        if merchant_reference_numbers:
            transactions_filters.update({'merchantReferenceNumbers': merchant_reference_numbers})
        if checkout_invoice_numbers:
            transactions_filters.update({'checkoutInvoiceNumbers': checkout_invoice_numbers})
        if capture_invoice_numbers:
            transactions_filters.update({'captureInvoiceNumbers': capture_invoice_numbers})
        transactions_response = self.call_api(self.transactions_url, data=transactions_filters)
        if transactions_response and 'transactions' in transactions_response:
            return transactions_response['transactions']
        return False

    def call_api(self, url=None, access_token=None, data=None):
        if not self.auth:
            return False
        if not url.lower().startswith('http'):
            url = '{0}{1}'.format(self.api_url, url)
        request = urllib2.Request(url)

        if access_token is None:
            access_token = self._get_access_token()
        request.add_header('Authorization', 'Bearer {0}'.format(access_token))
        if data:
            data = json.dumps(data)
            data_len = len(data)
            request.add_header('Content-Type', 'application/hal+json;charset=utf-8')
            request.add_header('Content-Length', data_len)
            request.add_data(data)
        elif data == '':
            request.method = 'POST'
            request.add_data('')
        request.add_header('Accept', 'application/json')
        try:
            response = urllib2.urlopen(request)
        except urllib2.HTTPError as e:
            logger = logging.getLogger(__name__)
            fp = e.fp
            body = fp.read()
            fp.close()
            if hasattr(e, 'code'):
                print "Paydirekt Error {0}({1}): {2}".format(e.code, e.msg, body)
                logger.error("Paydirekt Error {0}({1}): {2}".format(e.code, e.msg, body))
            else:
                print "Paydirekt Error({0}): {1}".format(e.msg, body)
                logger.error("Paydirekt Error({0}): {1}".format(e.msg, body))
        else:
            return json.load(response)
        return False

    def _get_access_token(self):
        data = {
            'grantType': 'api_key',
        }

        request_id = str(uuid.uuid4())
        timestamp = time.time()
        formatted_timestamp_secret = self._format_timestamp_for_secret(timestamp)
        formatted_timestamp_header = self._format_timestamp_for_header(timestamp)
        random_nonce = self._get_random()

        # generate signature
        signature_plain = '{0}:{1}:{2}:{3}'.format(request_id, formatted_timestamp_secret, self.auth['API_KEY'],
                                                   random_nonce)

        signature = base64.urlsafe_b64encode(hmac.new(
            base64.urlsafe_b64decode(bytes(self.auth['API_SECRET'])),
            bytes(signature_plain),
            hashlib.sha256
        ).digest())

        request = urllib2.Request(url = '{0}{1}'.format(self.api_url, self.token_obtain_url))
        # preparing request
        request.add_header('X-Date', formatted_timestamp_header)
        request.add_header('X-Request-ID', request_id)
        data.update({'randomNonce': random_nonce})

        request.add_header('X-Auth-Key', self.auth['API_KEY'])
        request.add_header('X-Auth-Code', signature)
        data = json.dumps(data)
        data_len = len(data)
        request.add_header('Content-Type', 'application/hal+json;charset=utf-8')
        request.add_header('Accept', 'application/hal+json')
        request.add_header('Content-Length', data_len)
        request.add_data(data)

        try:
            response = urllib2.urlopen(request)
        except urllib2.HTTPError as e:
            logger = logging.getLogger(__name__)
            fp = e.fp
            body = fp.read()
            fp.close()
            if hasattr(e, 'code'):
                logger.error("Paydirekt Error {0}({1}): {2}".format(e.code, e.msg, body))
            else:
                logger.error("Paydirekt Error({0}): {1}".format(e.msg, body))
        else:
            return json.load(response)['access_token']

    def _format_timestamp_for_header(self, timestamp):
        weekdayname = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        monthname = [None, 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        year, month, day, hh, mm, ss, wd, y, z = time.gmtime(timestamp)
        s = "%s, %02d %3s %4d %02d:%02d:%02d GMT" % (weekdayname[wd], day, monthname[month], year, hh, mm, ss)
        return s

    def _format_timestamp_for_secret(self, timestamp):
        year, month, day, hh, mm, ss, wd, y, z = time.gmtime(timestamp)
        s = "%4d%02d%02d%02d%02d%02d" % (year, month, day, hh, mm, ss)
        return s

    def _get_random(self, length=64):
        valid_chars = string.ascii_letters + string.digits + '-' + '_'
        return ''.join(random.SystemRandom().choice(valid_chars) for x in range(length))
