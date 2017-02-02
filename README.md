# django-paydirekt

## How to install django-paydirekt?

There are just two steps needed to install django-paydirekt:

1. Install django-sofortueberweisung to your virtual env:

	```bash
	pip install django-paydirekt
	```

2. Configure your django installation with the following lines:

	```python
    # django-paydirekt
INSTALLED_APPS += ('django_paydirekt', )

PAYDIREKT_API_KEY = "e81d298b-60dd-4f46-9ec9-1dbc72f5b5df"
PAYDIREKT_API_SECRET = "GJlN718sQxN1unxbLWHVlcf0FgXw2kMyfRwD0mgTRME="

PAYDIREKT_SUCCESS_URL = "/"
PAYDIREKT_CANCELLATION_URL = "/"
PAYDIREKT_REJECTION_URL = "/"
PAYDIREKT_NOTIFICATION_URL = "/paydirekt/notifiy/"

PAYDIREKT_SANDBOX = True

PAYDIREKT_VALID_CHECKOUT_STATUS = ['OPEN', 'PENDING', 'APPROVED']
PAYDIREKT_VALID_CAPTURE_STATUS = ['OPEN', 'PENDING', 'APPROVED']
	```

3. Use methods for initialization and updating transaction where you need it:

    Initialization:

	```python
    paydirekt_wrapper = PaydirektWrapper(auth={
                            'API_SECRET': settings.PAYDIREKT_API_SECRET,
                            'API_KEY': settings.PAYDIREKT_API_KEY,
                        })
    paydirekt_wrapper.init(total_amount='10.00', reference_number='abc',)
	```

    Include the notification View in your URLs:

	```python
    # urls.py
    from django.conf.urls import include, url

    urlpatterns = [
        url('^paydirekt/', include('django_paydirekt.urls')),
    ]
	```

## What do you need for django-sofortueberweisung?

1. An merchant account on paydirekt.de
2. Django >= 1.5
