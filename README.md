# django-paydirekt [![Build Status](https://travis-ci.org/ParticulateSolutions/django-paydirekt.svg?branch=master)](https://travis-ci.org/ParticulateSolutions/django-paydirekt)

`django-paydirekt` is a lightweight [django](http://djangoproject.com) plugin which provides the integration of the payment service [paydirekt](https://www.paydirekt.de/).

## How to install django-paydirekt?

There are just two steps needed to install django-paydirekt:

1. Install django-paydirekt to your virtual env:

	```bash
	pip install django-paydirekt
	```

2. Configure your django installation with the following lines:

	```python
    # django-paydirekt
    INSTALLED_APPS += ('django_paydirekt', )

    PAYDIREKT = True
    PAYDIREKT_ROOT_URL = 'http://example.com'

    # Those are dummy test data - change to your data
    PAYDIREKT_API_KEY = "Your-Paydirekt-API-key"
    PAYDIREKT_API_SECRET = "Your-Paydirekt-API-secret"
	```

    There is a list of other settings you could set down below.

3. Include the notification View in your URLs:

	```python
    # urls.py
    from django.conf.urls import include, url

    urlpatterns = [
        url('^paydirekt/', include('django_paydirekt.urls')),
    ]
	```

## What do you need for django-paydirekt?

1. An merchant account on paydirekt.de
2. Django >= 1.8

## Usage

### Minimal Checkout init example:

```python
paydirekt_wrapper = PaydirektWrapper(auth={
    'API_SECRET': settings.PAYDIREKT_API_SECRET,
    'API_KEY': settings.PAYDIREKT_API_KEY,
})
paydirekt_checkout = paydirekt_wrapper.init(
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
```

### Example Capture

```python
paydirekt_capture = paydirekt_checkout.create_capture(
    amount=50,
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
```

### Example Refund

```python
paydirekt_refund = paydirekt_checkout.create_refund(
    amount=50,
    paydirekt_wrapper=self.paydirekt_wrapper,
    note='test',
    reason='Test2',
    reference_number='1',
    reconciliation_reference_number='2')
```

### Example Checokout-Close

```python
paydirekt_checkout.close()
paydirekt_checkout.close(paydirekt_wrapper)
```

### Example transaction

```python
paydirekt_wrapper = PaydirektWrapper(auth={
    'API_SECRET': settings.PAYDIREKT_API_SECRET,
    'API_KEY': settings.PAYDIREKT_API_KEY,
})
transactions = paydirekt_wrapper.transactions()
for transaction in transactions:
    # do something
```

## Customize

You may want to customize django-paydirekt to fit your needs.

### Settings

The first and most straight forward way to customize it, is to adjust the settings.

```python
PAYDIREKT_API_KEY = "Your-Paydirekt-API-key"
PAYDIREKT_API_SECRET = "Your-Paydirekt-API-secret"

PAYDIREKT_ROOT_URL = 'https://example.com'

PAYDIREKT_API_URL = getattr(settings, 'PAYDIREKT_API_URL', 'https://api.paydirekt.de')
PAYDIREKT_SANDBOX_API_URL = getattr(settings, 'PAYDIREKT_API_URL', 'https://api.sandbox.paydirekt.de')
PAYDIREKT_SANDBOX = getattr(settings, 'PAYDIREKT_SANDBOX', True)

PAYDIREKT_CHECKOUTS_URL = getattr(settings, 'PAYDIREKT_CHECKOUTS_URL', '/api/checkout/v1/checkouts')
PAYDIREKT_TOKEN_OBTAIN_URL = getattr(settings, 'PAYDIREKT_TOKEN_OBTAIN_URL', '/api/merchantintegration/v1/token/obtain')
PAYDIREKT_TRANSACTION_URL = getattr(settings, 'PAYDIREKT_TRANSACTION_URL', '/api/reporting/v1/reports/transactions')

PAYDIREKT_VALID_CAPTURE_STATUS = getattr(settings, 'PAYDIREKT_VALID_CAPTURE_STATUS', ['PENDING', 'SUCCESSFUL', 'REJECTED'])
PAYDIREKT_VALID_CHECKOUT_STATUS = getattr(settings, 'PAYDIREKT_VALID_CHECKOUT_STATUS', ['OPEN', 'PENDING', 'APPROVED', 'REJECTED', 'CANCELED', 'CLOSED', 'EXPIRED'])
PAYDIREKT_VALID_REFUND_STATUS = getattr(settings, 'PAYDIREKT_VALID_REFUND_STATUS', ['PENDING', 'SUCCESSFUL', 'ERROR', 'FAILED'])

PAYDIREKT_SHIPPING_OPTIONS = [{
    'code': 'DHL_PAKET',
    'name': 'DHL Paket',
    'description': 'Lieferung innerhalb von 1-3 Werktagen',
    'amount': 6.99
}]

# checkout urls
PAYDIREKT_SUCCESS_URL = getattr(settings, 'PAYDIREKT_SUCCESS_URL', '/')
PAYDIREKT_REJECTION_URL = getattr(settings, 'PAYDIREKT_REJECTION_URL', '/')
PAYDIREKT_CANCELLATION_URL = getattr(settings, 'PAYDIREKT_CANCELLATION_URL', '/')
PAYDIREKT_NOTIFICATION_URL = getattr(settings, 'PAYDIREKT_NOTIFICATION_URL', '/paydirekt/notify/')

# express
PAYDIREKT_VALID_COUNTRY_CODES = getattr(settings, 'PAYDIREKT_VALID_COUNTRY_CODES', ['DE'])
PAYDIREKT_VALID_ZIP_CODES = getattr(settings, 'PAYDIREKT_VALID_COUNTRY_CODES', ['*'])
PAYDIREKT_VALID_PACKSTATION = getattr(settings, 'PAYDIREKT_VALID_PACKSTATION', True)
PAYDIREKT_SHIPPING_TERMS_URL = getattr(settings, 'PAYDIREKT_SHIPPING_TERMS_URL', '/')
```

### Method overrides

There are a few methods in the NotificationView you may want to override to match your system.

```python
class MyNotifyPaydirektView(NotifyPaydirektView):
    # For express checkout you may want to set the rules for valid destinations
    def check_destinations(self, paydirekt_checkout, request_data, request):
        # do fancy stuff in here
        links = {'self': {'href': request.path}}
        return HttpResponse({'checkedDestinations': [], '_links': links}, status=200, content_type='application/hal+json;charset=UTF-8')

    # For all checkouts you want to customize the status callback method
    def handle_updated_checkout(self, paydirekt_checkout, expected_status=None):
        updated_checkout = paydirekt_checkout
        # Be sure to check whether the paydirekt status is the same as in the notification for security reasons
        if updated_checkout.refresh_from_paydirekt(self.paydirekt_wrapper, expected_status=expected_status):
            if updated_checkout.status not in settings.PAYDIREKT_VALID_CHECKOUT_STATUS:
                # do something
                return HttpResponse(status=400)
            # do something else
            return HttpResponse(status=200)
        return HttpResponse(status=400)

    # For captures you may want to do the same
    def handle_updated_capture(self, paydirekt_capture, expected_status=None):
        updated_capture = paydirekt_capture
        # Be sure to check whether the paydirekt status is the same as in the notification for security reasons
        if updated_capture.refresh_from_paydirekt(self.paydirekt_wrapper, expected_status=expected_status):
            if updated_capture.status not in settings.PAYDIREKT_VALID_CAPTURE_STATUS:
                # do something
                return HttpResponse(status=400)
            # do something else
            return HttpResponse(status=200)
        return HttpResponse(status=400)
```

### Sandbox/Production Switch

You may want to use Paydirekt on Staging before you switch to Production, without deploying new code.
You can achieve that by setting the sandbox keyword argument of the wrapper init method to False for sandbox.
This way your settings may contain `PAYDIREKT_SANDBOX=False` and you can test your application before production usage.
```python
paydirekt_wrapper = PaydirektWrapper(auth={
    'API_SECRET': 'sandbox-api-secret',
    'API_KEY': 'sandbox-api-key'
}, sandbox=True)
```

## Copyright and license

Copyright 2016-2018 Jonas Braun for Particulate Solutions GmbH, under [MIT license](https://github.com/minddust/bootstrap-progressbar/blob/master/LICENSE).
