# Django settings for testproject project.
from django.conf import settings

settings.configure(
    ALLOWED_HOSTS=['*'],
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:'
        }
    },
    ROOT_URLCONF='tests.test_urls',
    INSTALLED_APPS=(
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.staticfiles',
        'django_paydirekt',
        'tests',
    ),
    PAYDIREKT_API_KEY="e81d298b-60dd-4f46-9ec9-1dbc72f5b5df",
    PAYDIREKT_API_SECRET="GJlN718sQxN1unxbLWHVlcf0FgXw2kMyfRwD0mgTRME=",
    
    PAYDIREKT_SUCCESS_URL="/",
    PAYDIREKT_CANCELLATION_URL="/",
    PAYDIREKT_REJECTION_URL="/",
    PAYDIREKT_NOTIFICATION_URL="/paydirekt/notifiy/",

    PAYDIREKT_SANDBOX=True,

    PAYDIREKT_VALID_CHECKOUT_STATUS=['OPEN', 'PENDING', 'APPROVED'],
    PAYDIREKT_VALID_CAPTURE_STATUS=['PENDING', 'SUCCESSFUL']
)
