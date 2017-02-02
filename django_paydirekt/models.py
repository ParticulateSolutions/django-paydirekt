import base64
import hashlib
import hmac
import json
import logging
import random
import string
import urllib2
import uuid
import time

from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import ugettext_lazy as _


class PaydirektCheckout(models.Model):
    checkout_id = models.CharField(_("checkout id"), max_length=255, unique=True)
    payment_type = models.CharField(_("checkout id"), max_length=255, unique=True)
    total_amount = models.DecimalField(_("total amount"), max_digits=9, decimal_places=2)
    status = models.CharField(_("status"), max_length=255, blank=True)
    link = models.URLField(_("link"))
    approve_link = models.URLField(_("approve link"))
    close_link = models.URLField(_("close link"), blank=True)
    captures_link = models.URLField(_("captures link"), blank=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    last_modified = models.DateTimeField(_("last modified"), auto_now=True)

    objects = models.Manager()

    def __unicode__(self):
        return u"Paydirekt checkout: {}".format(self.checkout_id)

    def __str__(self):
        return "Paydirekt checkout: {}".format(self.checkout_id)

    class Meta:
        verbose_name = _("Paydirekt checkout")
        verbose_name_plural = _("Paydirekt checkouts")
        ordering = ["-created_at"]

    def create_capture(self,
                       amount,
                       wrapper,
                       note=None,
                       final=False,
                       reference_number=None,
                       reconciliation_reference_number=None,
                       invoice_reference_number=None,
                       notification_url=None,
                       delivery_information=None):
        capture_data = {
            'amount': amount,
        }
        if final:
            capture_data.update({'finalCapture': final})
        if note:
            capture_data.update({'note': note})
        if reference_number:
            capture_data.update({'merchantCaptureReferenceNumber': reference_number})
        if reconciliation_reference_number:
            capture_data.update({'merchantReconciliationReferenceNumber': reconciliation_reference_number})
        if invoice_reference_number:
            capture_data.update({'captureInvoiceReferenceNumber': invoice_reference_number})
        if notification_url:
            notification_url = wrapper._build_full_uri(notification_url)
            capture_data.update({'callbackUrlStatusUpdates': notification_url})
        if delivery_information:
            capture_data.update({'deliveryInformation': delivery_information})

        capture_response = wrapper._call_api(url=self.captures_link, access_token=wrapper._get_access_token(), data=capture_data)

        if capture_response and 'amount' in capture_response and capture_response['amount'] == float(amount):
            return PaydirektCapture.objects.create(checkout=self,
                                                   amount=amount,
                                                   final=final,
                                                   transaction_id=capture_response['transactionId'],
                                                   status=capture_response['status'],
                                                   link=capture_response['_links']['self']['href'],
                                                   capture_type=capture_response['type'])
        else:
            return False


class PaydirektCapture(models.Model):
    checkout = models.ForeignKey(PaydirektCheckout, verbose_name=_("checkout"), related_name='captures')
    amount = models.DecimalField(_("total amount"), max_digits=9, decimal_places=2)
    transaction_id = models.CharField(_("transaction id"), max_length=255, unique=True)
    final = models.BooleanField(_("final"), default=False)
    link = models.URLField(_("link"))
    status = models.CharField(_("status"), max_length=255, blank=True)
    capture_type = models.CharField(_("capture type"), max_length=255, blank=True)

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    last_modified = models.DateTimeField(_("last modified"), auto_now=True)

    objects = models.Manager()

    def __unicode__(self):
        return u"Paydirekt checkout: {}".format(self.checkout_id)

    def __str__(self):
        return "Paydirekt checkout: {}".format(self.checkout_id)

    class Meta:
        verbose_name = _("Paydirekt checkout")
        verbose_name_plural = _("Paydirekt checkouts")
        ordering = ["-created_at"]


class PaydirektWrapper(object):

    token_obtain_url = '/api/merchantintegration/v1/token/obtain'
    checkouts_url = '/api/checkout/v1/checkouts'
    api_url = 'https://api.paydirekt.de'
    sandbox_url = 'https://api.sandbox.paydirekt.de'
    interface_version = 'django_paydirekt_v0.1.0'
    auth = None

    def __init__(self, auth=None):
        super(PaydirektWrapper, self).__init__()
        self.auth = auth
        if settings.PAYDIREKT_SANDBOX:
            self.api_url = self.sandbox_url

    def init(self, total_amount, reference_number,
             email_address=None,
             payment_type='DIRECT_SALE',
             currency_code='EUR',
             success_url=settings.PAYDIREKT_SUCCESS_URL,
             cancellation_url=settings.PAYDIREKT_CANCELLATION_URL,
             rejection_url=settings.PAYDIREKT_REJECTION_URL,
             notification_url=None,
             note=None,
             shipping_amount=None,
             order_amount=None,
             overcapture=False,
             shopping_cart_type=None,
             delivery_information=None,
             delivery_type=None,
             shipping_address=None,
             invoice_reference_number=None,
             reconciliation_reference_number=None,
             minimum_age=None,
             minimum_age_fail_url=None,
             items=None,
             customer_number=None):

        if payment_type != 'DIRECT_SALE' and payment_type != 'ORDER':
            raise RuntimeError('Unsupported Payment Type.')

        success_url = self._build_full_uri(success_url)
        cancellation_url = self._build_full_uri(cancellation_url)
        rejection_url = self._build_full_uri(rejection_url)

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

        # optional fields
        if notification_url:
            notification_url = self._build_full_uri(notification_url)
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
        if delivery_information:
            checkout_data.update({'deliveryInformation': delivery_information})
        if delivery_type:
            checkout_data.update({'deliveryType': delivery_type})
        if shipping_address:
            checkout_data.update({'shippingAddress': shipping_address})
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

        checkout_response = self._call_api(url=self.checkouts_url, access_token=self._get_access_token(), data=checkout_data)
        if checkout_response and 'totalAmount' in checkout_response and checkout_response['totalAmount'] == float(total_amount):
            checkout_id = checkout_response['checkoutId']
            status = checkout_response['status']
            approve_link = checkout_response['_links']['approve']['href']
            link = checkout_response['_links']['self']['href']
            return PaydirektCheckout.objects.create(payment_type=payment_type,
                                                    total_amount=total_amount,
                                                    checkout_id=checkout_id,
                                                    status=status,
                                                    approve_link=approve_link,
                                                    link=link)
        return False

    def update_checkout(self, paydirekt_checkout, expected_status=None):
        checkout_response = self._call_api(url=paydirekt_checkout.link, access_token=self._get_access_token())
        if not checkout_response:
            logger = logging.getLogger(__name__)
            logger.error("Paydirekt Approval URL not available")
            return False

        if expected_status and expected_status != checkout_response['status']:
            logger = logging.getLogger(__name__)
            logger.error("Paydirekt Status Error: expected: {}, found: {}".format(expected_status, checkout_response['status']))
            return False

        paydirekt_checkout.status = checkout_response['status']

        if paydirekt_checkout.payment_type == 'ORDER' and paydirekt_checkout.status == 'APPROVED':
            paydirekt_checkout.close_link = checkout_response['_links']['close']['href']
            paydirekt_checkout.captures_link = checkout_response['_links']['captures']['href']
        paydirekt_checkout.save()
        return paydirekt_checkout

    def _get_access_token(self):
        obtain_token_data = {
            'grantType': 'api_key',
        }
        obtain_token_response = self._call_api(url=self.token_obtain_url, data=obtain_token_data)
        access_token = obtain_token_response['access_token']
        return access_token

    def _call_api(self, url=None, access_token=None, data=None):
        if not url.lower().startswith('http'):
            url = '{}{}'.format(self.api_url, url)
        request = urllib2.Request(url)

        if access_token is None:
            request_id = str(uuid.uuid4())
            timestamp = time.time()
            formatted_timestamp_secret = self._format_timestamp_for_secret(timestamp)
            formatted_timestamp_header = self._format_timestamp_for_header(timestamp)
            random_nonce = self._get_random()

            # generate signature
            signature_plain = '{}:{}:{}:{}'.format(request_id, formatted_timestamp_secret, self.auth['API_KEY'], random_nonce)

            signature = base64.urlsafe_b64encode(hmac.new(
                base64.urlsafe_b64decode(bytes(self.auth['API_SECRET'])),
                bytes(signature_plain),
                hashlib.sha256
            ).digest())

            # preparing request
            request.add_header('X-Date', formatted_timestamp_header)
            request.add_header('X-Request-ID', request_id)
            if data:
                data.update({'randomNonce': random_nonce})
            else:
                data = {'randomNonce': random_nonce}

            if self.auth:
                request.add_header('X-Auth-Key', self.auth['API_KEY'])
                request.add_header('X-Auth-Code', signature)
        else:
            request.add_header('Authorization', 'Bearer {0}'.format(access_token))
        if data:
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
                logger.error("Paydirekt Error {}({}): {}".format(e.code, e.msg, body))
            else:
                logger.error("Paydirekt Error({}): {}".format(e.msg, body))
        else:
            return json.load(response)
        return False

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
        valid_chars = string.ascii_uppercase + string.ascii_lowercase + string.digits + '-' + '_'
        return ''.join(random.choice(valid_chars) for x in range(length))

    def _build_full_uri(self, url):
        if url.startswith('/'):
            site = Site.objects.get_current().domain
            protocol = 'http'
            try:
                if settings.PAYDIRKET_USE_SSL:
                    protocol = 'https'
            except:
                pass
            url = '{protocol}://{site}{path}'.format(protocol=protocol, site=site, path=url)
        return url
