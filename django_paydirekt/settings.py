from __init__ import __version__

from django.conf import settings

DJANGO_PAYDIREKT_VERSION = __version__

PAYDIREKT_ROOT_URL = 'https://example.com'

PAYDIREKT_API_URL = getattr(settings, 'PAYDIREKT_API_URL', 'https://api.paydirekt.de')
PAYDIREKT_SANDBOX_API_URL = getattr(settings, 'PAYDIREKT_API_URL', 'https://api.sandbox.paydirekt.de')
PAYDIREKT_SANDBOX = getattr(settings, 'PAYDIREKT_SANDBOX', True)

PAYDIREKT_CHECKOUTS_URL = getattr(settings, 'PAYDIREKT_CHECKOUTS_URL', '/api/checkout/v1/checkouts')
PAYDIREKT_TOKEN_OBTAIN_URL = getattr(settings, 'PAYDIREKT_TOKEN_OBTAIN_URL', '/api/merchantintegration/v1/token/obtain')

PAYDIREKT_VALID_CAPTURE_STATUS = getattr(settings, 'PAYDIREKT_VALID_CAPTURE_STATUS', ['PENDING', 'SUCCESSFUL'])
PAYDIREKT_VALID_CHECKOUT_STATUS = getattr(settings, 'PAYDIREKT_VALID_CHECKOUT_STATUS', ['OPEN', 'PENDING', 'APPROVED'])