#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json
import logging
import os
import time
import urllib2

from pip._vendor.requests import Response

from django.conf import settings
from django.conf.urls import include, patterns, url
from django.test import Client, TestCase
from django_paydirekt.models import PaydirektCheckout
from testfixtures import replace

from django_paydirekt.wrappers import PaydirektWrapper
from .test_response_mockups import TEST_RESPONSES

urlpatterns = patterns('',
    url('^paydirekt/', include('django_paydirekt.urls', namespace='paydirekt', app_name='paydirekt')),
)


def mock_generate_uuid(length=12):
    return '12345678901234567890'


def mock_urlopen(request):
    response = {}
    url = request.get_full_url()
    try:
        if url == 'https://api.sandbox.paydirekt.de/api/merchantintegration/v1/token/obtain':
            response = TEST_RESPONSES['token_obtain']
        if url == 'https://api.sandbox.paydirekt.de/api/checkout/v1/checkouts/123-abc-approved/':
            response = TEST_RESPONSES['status_approved']
        if url == 'https://api.sandbox.paydirekt.de/api/checkout/v1/checkouts/123-abc-expired/':
            response = TEST_RESPONSES['status_expired']
        if url == 'https://api.sandbox.paydirekt.de/api/checkout/v1/checkouts/123-abc-approved-minimal/':
            response = TEST_RESPONSES['minimal_status_approved']
    except KeyError:
        response = False
    result = MockResponse(response)
    return result


class MockResponse(Response):
    response = ''

    def __init__(self, response):
        super(MockResponse, self).__init__()
        if not response:
            self.status_code = 404
        self.response = json.dumps(response)

    def read(self):
        return self.response


class TestPaydirektNotifications(TestCase):
    paydirekt_wrapper = None

    def setUp(self):
        self.paydirekt_wrapper = PaydirektWrapper(auth={
            'API_SECRET': settings.PAYDIREKT_API_SECRET,
            'API_KEY': settings.PAYDIREKT_API_KEY,
        })

    # testing valid checkout
    @replace('django_paydirekt.wrappers.urllib2.urlopen', mock_urlopen)
    def test_get_notify(self):
        client = Client()
        response = client.get('/paydirekt/notify/')
        self.assertEqual(response.status_code, 405)

    @replace('django_paydirekt.wrappers.urllib2.urlopen', mock_urlopen)
    def test_notify_callback_unknown_checkout(self):
        client = Client()
        post_data = {'checkoutId': '123-abc-notfound1', 'merchantOrderReferenceNumber': '123-abc-notfound1', 'checkoutStatus': 'OPEN'}
        response = client.post('/paydirekt/notify/', data=json.dumps(post_data), content_type='application/hal+json')
        self.assertEqual(response.status_code, 400)

    @replace('django_paydirekt.wrappers.urllib2.urlopen', mock_urlopen)
    def test_known_checkout_unknown_at_paydirekt(self):
        client = Client()
        self._create_test_checkout(checkout_id='123-abc-notfound-paydirekt')
        post_data = {'checkoutId': '123-abc-notfound-paydirekt', 'merchantOrderReferenceNumber': '123-abc-notfound-paydirekt', 'checkoutStatus': 'APPROVED'}
        response = client.post('/paydirekt/notify/', data=json.dumps(post_data), content_type='application/hal+json')
        self.assertEqual(response.status_code, 400)

    @replace('django_paydirekt.wrappers.urllib2.urlopen', mock_urlopen)
    def test_known_checkout_known_at_paydirekt_correct_status(self):
        client = Client()
        self._create_test_checkout(checkout_id='123-abc-approved')
        post_data = {'checkoutId': '123-abc-approved', 'merchantOrderReferenceNumber': '123-abc-approved', 'checkoutStatus': 'APPROVED'}
        response = client.post('/paydirekt/notify/', data=json.dumps(post_data), content_type='application/hal+json')
        self.assertEqual(response.status_code, 200)

    @replace('django_paydirekt.wrappers.urllib2.urlopen', mock_urlopen)
    def test_known_checkout_known_at_paydirekt_correct_status_minimal(self):
        client = Client()
        self._create_test_checkout(checkout_id='123-abc-approved-minimal')
        post_data = {'checkoutId': '123-abc-approved-minimal', 'merchantOrderReferenceNumber': '123-abc-approved-minimal', 'checkoutStatus': 'APPROVED'}
        response = client.post('/paydirekt/notify/', data=json.dumps(post_data), content_type='application/hal+json')
        self.assertEqual(response.status_code, 200)

    @replace('django_paydirekt.wrappers.urllib2.urlopen', mock_urlopen)
    def test_known_checkout_known_at_paydirekt_incorrect_status(self):
        client = Client()
        self._create_test_checkout(checkout_id='123-abc-expired')
        post_data = {'checkoutId': '123-abc-expired', 'merchantOrderReferenceNumber': '123-abc-expired', 'checkoutStatus': 'APPROVED'}
        response = client.post('/paydirekt/notify/', data=json.dumps(post_data), content_type='application/hal+json')
        self.assertEqual(response.status_code, 400)

    def _create_test_checkout(self, checkout_id):
        return PaydirektCheckout.objects.create(total_amount=1.0,
                                                checkout_id=checkout_id,
                                                status='OPEN',
                                                link='https://api.sandbox.paydirekt.de/api/checkout/v1/checkouts/'+checkout_id+'/',
                                                approve_link ='https://sandbox.paydirekt.de/checkout/#/checkout/'+checkout_id)


class TestPaydirektCheckouts(TestCase):
    paydirekt_wrapper = None

    def setUp(self):
        self.paydirekt_wrapper = PaydirektWrapper(auth={
            'API_SECRET': settings.PAYDIREKT_API_SECRET,
            'API_KEY': settings.PAYDIREKT_API_KEY,
        })

    def test_minimal_valid_anonymous_donation_checkout(self):
        paydirekt_checkout = self.paydirekt_wrapper.init(
            total_amount=1.00,
            reference_number='1',
            shopping_cart_type='ANONYMOUS_DONATION')
        self.assertEqual(paydirekt_checkout.status, 'OPEN')
        self.assertEqual(paydirekt_checkout.total_amount, 1.00)

    def test_minimal_valid_direct_sale_checkout(self):
        paydirekt_checkout = self.paydirekt_wrapper.init(
            total_amount=1.00,
            reference_number='1',
            payment_type='DIRECT_SALE',
            shipping_address={
                'addresseeGivenName': 'Hermann',
                'addresseeLastName': 'Meyer',
                'street': 'Wieseneckstraße',
                'streetNr': '26',
                'zip': '90571',
                'city': 'Schwaig bei Nürnberg',
                'countryCode': 'DE'
            }
        )
        self.assertEqual(paydirekt_checkout.status, 'OPEN')
        self.assertEqual(paydirekt_checkout.total_amount, 1.00)

    def test_full_valid_direct_sale_checkout(self):
        paydirekt_checkout = self.paydirekt_wrapper.init(
            payment_type='DIRECT_SALE',
            total_amount=100,
            shipping_amount=3.5,
            order_amount=96.5,
            email_address='max@muster.de',
            customer_number=123,
            reconciliation_reference_number=124,
            reference_number=125,
            invoice_reference_number=126,
            note='Your Test at django-paydirekt.',
            minimum_age=18,
            currency_code='EUR',
            overcapture=False,
            delivery_type='STANDARD',
            delivery_information={
                "expectedShippingDate": "2016-10-19T12:00:00Z",
                "logisticsProvider": "DHL",
                "trackingNumber": "1234567890"
            },
            shipping_address={
                'addresseeGivenName': 'Hermann',
                'addresseeLastName': 'Meyer',
                'street': 'Wieseneckstraße',
                'streetNr': '26',
                'zip': '90571',
                'city': 'Schwaig bei Nürnberg',
                'countryCode': 'DE'
            },
            items=[
                {
                    'quantity': 3,
                    'name': 'Bobbycar',
                    'ean': '800001303',
                    'price': 25.99
                },
                {
                    'quantity': 1,
                    'name': 'Helm',
                    'price': 18.53
                }
            ]
        )
        self.assertEqual(paydirekt_checkout.status, 'OPEN')
        self.assertEqual(paydirekt_checkout.total_amount, 100)

        paydirekt_checkout.refresh_from_paydirekt(self.paydirekt_wrapper, expected_status='OPEN')

        paydirekt_checkout.refresh_from_db()
        self.assertEqual(paydirekt_checkout.status, 'OPEN')

    def test_full_valid_order_checkout_full_with_notification(self):
        paydirekt_checkout = self.paydirekt_wrapper.init(
            payment_type='ORDER',
            total_amount=100,
            shipping_amount=3.5,
            order_amount=96.5,
            email_address='max@muster.de',
            customer_number=123,
            reconciliation_reference_number=124,
            reference_number=125,
            invoice_reference_number=126,
            note='Your Test at django-paydirekt.',
            minimum_age=18,
            currency_code='EUR',
            overcapture=False,
            delivery_type='STANDARD',
            delivery_information={
                "expectedShippingDate": "2016-10-19T12:00:00Z",
                "logisticsProvider": "DHL",
                "trackingNumber": "1234567890"
            },
            shipping_address={
                'addresseeGivenName': 'Hermann',
                'addresseeLastName': 'Meyer',
                'street': 'Wieseneckstraße',
                'streetNr': '26',
                'zip': '90571',
                'city': 'Schwaig bei Nürnberg',
                'countryCode': 'DE'
            },
            items=[
                {
                    'quantity': 3,
                    'name': 'Bobbycar',
                    'ean': '800001303',
                    'price': 25.99
                },
                {
                    'quantity': 1,
                    'name': 'Helm',
                    'price': 18.53
                }
            ]
        )
        self.assertEqual(paydirekt_checkout.status, 'OPEN')
        self.assertEqual(paydirekt_checkout.total_amount, 100)
        test_customer = TestCustomer()
        test_customer.confirm_checkout(paydirekt_checkout)

        # give paydirekt time to approve
        time.sleep(10)

        client = Client()
        post_data = {'checkoutId': paydirekt_checkout.checkout_id, 'merchantOrderReferenceNumber': '', 'checkoutStatus': 'APPROVED'}
        client.post('/paydirekt/notify/', data=json.dumps(post_data), content_type='application/hal+json')
        paydirekt_checkout.refresh_from_db()
        self.assertEqual(paydirekt_checkout.status, 'APPROVED')

    def test_full_valid_order_checkout_full_with_manual_update(self):
        paydirekt_checkout = self.paydirekt_wrapper.init(
            payment_type='ORDER',
            total_amount=100,
            shipping_amount=3.5,
            order_amount=96.5,
            email_address='max@muster.de',
            customer_number=123,
            reconciliation_reference_number=124,
            reference_number=125,
            invoice_reference_number=126,
            note='Your Test at django-paydirekt.',
            minimum_age=18,
            currency_code='EUR',
            overcapture=False,
            delivery_type='STANDARD',
            delivery_information={
                "expectedShippingDate": "2016-10-19T12:00:00Z",
                "logisticsProvider": "DHL",
                "trackingNumber": "1234567890"
            },
            shipping_address={
                'addresseeGivenName': 'Hermann',
                'addresseeLastName': 'Meyer',
                'street': 'Wieseneckstraße',
                'streetNr': '26',
                'zip': '90571',
                'city': 'Schwaig bei Nürnberg',
                'countryCode': 'DE'
            },
            items=[
                {
                    'quantity': 3,
                    'name': 'Bobbycar',
                    'ean': '800001303',
                    'price': 25.99
                },
                {
                    'quantity': 1,
                    'name': 'Helm',
                    'price': 18.53
                }
            ]
        )
        self.assertEqual(paydirekt_checkout.status, 'OPEN')
        self.assertEqual(paydirekt_checkout.total_amount, 100)
        test_customer = TestCustomer()
        test_customer.confirm_checkout(paydirekt_checkout)

        paydirekt_checkout.refresh_from_paydirekt(self.paydirekt_wrapper, expected_status='APPROVED')

        paydirekt_checkout.refresh_from_db()
        self.assertEqual(paydirekt_checkout.status, 'APPROVED')
        self.assertNotEqual(paydirekt_checkout.close_link, '')
        self.assertNotEqual(paydirekt_checkout.captures_link, '')

    def test_full_valid_direct_sale_checkout_full_with_notification(self):
        paydirekt_checkout = self.paydirekt_wrapper.init(
            payment_type='DIRECT_SALE',
            total_amount=100,
            shipping_amount=3.5,
            order_amount=96.5,
            email_address='max@muster.de',
            customer_number=123,
            reconciliation_reference_number=124,
            reference_number=125,
            invoice_reference_number=126,
            note='Your Test at django-paydirekt.',
            minimum_age=18,
            currency_code='EUR',
            overcapture=False,
            delivery_type='STANDARD',
            delivery_information={
                "expectedShippingDate": "2016-10-19T12:00:00Z",
                "logisticsProvider": "DHL",
                "trackingNumber": "1234567890"
            },
            shipping_address={
                'addresseeGivenName': 'Hermann',
                'addresseeLastName': 'Meyer',
                'street': 'Wieseneckstraße',
                'streetNr': '26',
                'zip': '90571',
                'city': 'Schwaig bei Nürnberg',
                'countryCode': 'DE'
            },
            items=[
                {
                    'quantity': 3,
                    'name': 'Bobbycar',
                    'ean': '800001303',
                    'price': 25.99
                },
                {
                    'quantity': 1,
                    'name': 'Helm',
                    'price': 18.53
                }
            ]
        )
        self.assertEqual(paydirekt_checkout.status, 'OPEN')
        self.assertEqual(paydirekt_checkout.total_amount, 100)
        test_customer = TestCustomer()
        test_customer.confirm_checkout(paydirekt_checkout)

        # give paydirekt time to approve
        time.sleep(10)

        client = Client()
        post_data = {'checkoutId': paydirekt_checkout.checkout_id, 'merchantOrderReferenceNumber': '', 'checkoutStatus': 'APPROVED'}
        client.post('/paydirekt/notify/', data=json.dumps(post_data), content_type='application/hal+json')
        paydirekt_checkout.refresh_from_db()
        self.assertEqual(paydirekt_checkout.status, 'APPROVED')

    def test_full_valid_direct_sale_checkout_full_with_manual_update(self):
        paydirekt_checkout = self.paydirekt_wrapper.init(
            payment_type='DIRECT_SALE',
            total_amount=100,
            shipping_amount=3.5,
            order_amount=96.5,
            email_address='max@muster.de',
            customer_number=123,
            reconciliation_reference_number=124,
            reference_number=125,
            invoice_reference_number=126,
            note='Your Test at django-paydirekt.',
            minimum_age=18,
            currency_code='EUR',
            overcapture=False,
            delivery_type='STANDARD',
            delivery_information={
                "expectedShippingDate": "2016-10-19T12:00:00Z",
                "logisticsProvider": "DHL",
                "trackingNumber": "1234567890"
            },
            shipping_address={
                'addresseeGivenName': 'Hermann',
                'addresseeLastName': 'Meyer',
                'street': 'Wieseneckstraße',
                'streetNr': '26',
                'zip': '90571',
                'city': 'Schwaig bei Nürnberg',
                'countryCode': 'DE'
            },
            items=[
                {
                    'quantity': 3,
                    'name': 'Bobbycar',
                    'ean': '800001303',
                    'price': 25.99
                },
                {
                    'quantity': 1,
                    'name': 'Helm',
                    'price': 18.53
                }
            ]
        )
        self.assertEqual(paydirekt_checkout.status, 'OPEN')
        self.assertEqual(paydirekt_checkout.total_amount, 100)
        test_customer = TestCustomer()
        test_customer.confirm_checkout(paydirekt_checkout)

        paydirekt_checkout.refresh_from_paydirekt(self.paydirekt_wrapper, expected_status='APPROVED')

        paydirekt_checkout.refresh_from_db()
        self.assertEqual(paydirekt_checkout.status, 'APPROVED')

    def test_create_capture_50_50(self):
        paydirekt_checkout = self.paydirekt_wrapper.init(
            payment_type='ORDER',
            total_amount=100,
            shipping_amount=3.5,
            order_amount=96.5,
            email_address='max@muster.de',
            customer_number=123,
            reconciliation_reference_number=124,
            reference_number=125,
            invoice_reference_number=126,
            note='Your Test at django-paydirekt.',
            minimum_age=18,
            currency_code='EUR',
            overcapture=False,
            delivery_type='STANDARD',
            delivery_information={
                "expectedShippingDate": "2016-10-19T12:00:00Z",
                "logisticsProvider": "DHL",
                "trackingNumber": "1234567890"
            },
            shipping_address={
                'addresseeGivenName': 'Hermann',
                'addresseeLastName': 'Meyer',
                'street': 'Wieseneckstraße',
                'streetNr': '26',
                'zip': '90571',
                'city': 'Schwaig bei Nürnberg',
                'countryCode': 'DE'
            },
            items=[
                {
                    'quantity': 3,
                    'name': 'Bobbycar',
                    'ean': '800001303',
                    'price': 25.99
                },
                {
                    'quantity': 1,
                    'name': 'Helm',
                    'price': 18.53
                }
            ]
        )
        self.assertEqual(paydirekt_checkout.status, 'OPEN')
        self.assertEqual(paydirekt_checkout.total_amount, 100)
        test_customer = TestCustomer()
        test_customer.confirm_checkout(paydirekt_checkout)

        paydirekt_checkout.refresh_from_paydirekt(self.paydirekt_wrapper, expected_status='APPROVED')

        paydirekt_checkout.refresh_from_db()
        self.assertEqual(paydirekt_checkout.status, 'APPROVED')
        paydirekt_capture = paydirekt_checkout.create_capture(amount=50,
                                                              wrapper=self.paydirekt_wrapper,
                                                              note='First payment',
                                                              final=False,
                                                              reference_number='Payment1',
                                                              reconciliation_reference_number='Payment1',
                                                              invoice_reference_number='Payment1',
                                                              notification_url='/',
                                                              delivery_information={
                                                                  "expectedShippingDate": "2016-10-19T12:00:00Z",
                                                                  "logisticsProvider": "DHL",
                                                                  "trackingNumber": "1234567890"
                                                              })
        self.assertEqual(paydirekt_capture.status, 'SUCCESSFUL')
        paydirekt_capture2 = paydirekt_checkout.create_capture(amount=50,
                                                               wrapper=self.paydirekt_wrapper,
                                                               note='Second payment',
                                                               final=True,
                                                               reference_number='Payment2',
                                                               reconciliation_reference_number='Payment2',
                                                               invoice_reference_number='Payment2',
                                                               notification_url='/',
                                                               delivery_information={
                                                                   "expectedShippingDate": "2016-10-19T12:00:00Z",
                                                                   "logisticsProvider": "DHL",
                                                                   "trackingNumber": "1234567890"
                                                               })
        self.assertEqual(paydirekt_capture2.status, 'SUCCESSFUL')

    def test_create_capture_too_high(self):
        paydirekt_checkout = self.paydirekt_wrapper.init(
            payment_type='ORDER',
            total_amount=100,
            shipping_amount=3.5,
            order_amount=96.5,
            email_address='max@muster.de',
            customer_number=123,
            reconciliation_reference_number=124,
            reference_number=125,
            invoice_reference_number=126,
            note='Your Test at django-paydirekt.',
            minimum_age=18,
            currency_code='EUR',
            overcapture=False,
            delivery_type='STANDARD',
            delivery_information={
                "expectedShippingDate": "2016-10-19T12:00:00Z",
                "logisticsProvider": "DHL",
                "trackingNumber": "1234567890"
            },
            shipping_address={
                'addresseeGivenName': 'Hermann',
                'addresseeLastName': 'Meyer',
                'street': 'Wieseneckstraße',
                'streetNr': '26',
                'zip': '90571',
                'city': 'Schwaig bei Nürnberg',
                'countryCode': 'DE'
            },
            items=[
                {
                    'quantity': 3,
                    'name': 'Bobbycar',
                    'ean': '800001303',
                    'price': 25.99
                },
                {
                    'quantity': 1,
                    'name': 'Helm',
                    'price': 18.53
                }
            ]
        )
        self.assertEqual(paydirekt_checkout.status, 'OPEN')
        self.assertEqual(paydirekt_checkout.total_amount, 100)
        test_customer = TestCustomer()
        test_customer.confirm_checkout(paydirekt_checkout)

        paydirekt_checkout.refresh_from_paydirekt(self.paydirekt_wrapper, expected_status='APPROVED')

        paydirekt_checkout.refresh_from_db()
        self.assertEqual(paydirekt_checkout.status, 'APPROVED')
        paydirekt_capture = paydirekt_checkout.create_capture(amount=120,
                                                              wrapper=self.paydirekt_wrapper,
                                                              note='First payment',
                                                              final=True,
                                                              reference_number='Payment1',
                                                              reconciliation_reference_number='Payment1',
                                                              invoice_reference_number='Payment1',
                                                              notification_url='/',
                                                              delivery_information={
                                                                  "expectedShippingDate": "2016-10-19T12:00:00Z",
                                                                  "logisticsProvider": "DHL",
                                                                  "trackingNumber": "1234567890"
                                                              })
        self.assertFalse(paydirekt_capture)


class TestCustomer(object):
    obtain_token_url = 'https://api.sandbox.paydirekt.de/api/accountuser/v1/token/obtain'
    checkout_confirm_url = 'https://api.sandbox.paydirekt.de/api/checkout/v1/checkouts/{checkoutId}/confirm'
    checkout_detail_url = 'https://api.sandbox.paydirekt.de/api/checkout/v1/checkouts/{checkoutId}'
    cafile = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), 'cacert.pem')

    def confirm_checkout(self, paydirekt_checkout):
        checkout_id = paydirekt_checkout.checkout_id

        # aquire token
        token = self._get_token(checkout_id)

        # fraud protection requires GET before APPROVE checkout
        checkout_specific_url = self.checkout_detail_url.format(checkoutId=checkout_id)
        request = urllib2.Request(checkout_specific_url)
        request.add_header('Authorization', 'Bearer {}'.format(token))
        request.add_header('Content-Type', 'application/hal+json;charset=utf-8')
        request.add_header('Accept', 'application/hal+json')
        request.add_header('User-Agent', 'Mozilla/5.0')
        try:
            response = urllib2.urlopen(request, cafile=self.cafile)
        except urllib2.HTTPError as e:
            logger = logging.getLogger(__name__)
            fp = e.fp
            body = fp.read()
            fp.close()
            raise AssertionError("Checkout GET ERROR {}({}): {}".format(e.code, e.msg, body))

        # approve checkout
        approve_checkout_url = self.checkout_confirm_url.format(checkoutId=checkout_id)
        request = urllib2.Request(approve_checkout_url)
        request.add_header('Authorization', 'Bearer {}'.format(token))
        request.add_header('Content-Type', 'application/hal+json;charset=utf-8')
        request.add_header('Accept', 'application/hal+json')
        request.add_header('User-Agent', 'Mozilla/5.0')
        request.add_data('')
        try:
            response = urllib2.urlopen(request, cafile=self.cafile)
        except urllib2.HTTPError as e:
            logger = logging.getLogger(__name__)
            fp = e.fp
            body = fp.read()
            fp.close()
            raise AssertionError("Paydirekt Error {}({}): {}".format(e.code, e.msg, body))
        else:
            return json.load(response)

    def _get_token(self, checkout_id):
        request = urllib2.Request(self.obtain_token_url)
        request.add_header('Authorization', 'Basic YnYtY2hlY2tvdXQtd2ViOjhjZEtIZVJ3eDNVNHI3WTlvQ0JkZ1A1OW5DdmNHTWRMa0NmQVNXdVZDdm8=')
        request.add_header('Content-Type', 'application/hal+json;charset=utf-8')
        request.add_header('Accept', 'application/hal+json')
        request.add_header('User-Agent', 'Mozilla/5.0')

        data = {
            'processId': checkout_id,
            'password': 'PHHrLCitIr3f7m7PFZbdxtmvirHhbJtch_XqUaSTXRrXWdIYBjfgpRA2ICM6qY7s',
            'username': 'github_testuser',
            'grantType': 'password'
        }
        request.add_data(json.dumps(data))
        try:
            response = urllib2.urlopen(request)
        except urllib2.HTTPError as e:
            logger = logging.getLogger(__name__)
            fp = e.fp
            body = fp.read()
            fp.close()
            raise AssertionError("Token Error {}({}): {}".format(e.code, e.msg, body))
        else:
            return json.load(response)['access_token']