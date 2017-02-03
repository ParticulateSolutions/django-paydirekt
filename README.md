# django-paydirekt

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

# Those are dummy test data - change to your data
PAYDIREKT_API_KEY = "Your-Paydirekt-API-key"
PAYDIREKT_API_SECRET = "Your-Paydirekt-API-secret"

PAYDIREKT_SUCCESS_URL = "/path/to/success/url/"
PAYDIREKT_CANCELLATION_URL = "/path/to/cancellation/url/"
PAYDIREKT_REJECTION_URL = "/path/to/rejection/url/"
PAYDIREKT_NOTIFICATION_URL = "/path/to/notifiy/"

PAYDIREKT_SANDBOX = True

PAYDIREKT_VALID_CHECKOUT_STATUS = ['OPEN', 'PENDING', 'APPROVED']
PAYDIREKT_VALID_CAPTURE_STATUS = ['OPEN', 'PENDING', 'SUCCESSFUL']
PAYDIREKT_VALID_REFUND_STATUS = ['PENDING', 'SUCCESSFUL']
	```

3. Use methods for initialization and updating transaction where you need it:

    Initialization:

	```python
    paydirekt_wrapper = PaydirektWrapper(auth={
                            'API_SECRET': settings.PAYDIREKT_API_SECRET,
                            'API_KEY': settings.PAYDIREKT_API_KEY,
                        })
    paydirekt_wrapper.init(
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

    Include the notification View in your URLs:

	```python
    # urls.py
    from django.conf.urls import include, url

    urlpatterns = [
        url('^paydirekt/', include('django_paydirekt.urls')),
    ]
	```

## What do you need for django-paydirekt?

1. An merchant account on paydirekt.de
2. Django >= 1.5
