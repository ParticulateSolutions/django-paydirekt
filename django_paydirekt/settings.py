from __init__ import __version__
from django.conf import settings

DJANGO_PAYDIREKT_VERSION = __version__

PAYDIREKT_API_SECRET = getattr(settings, 'PAYDIREKT_API_SECRET', False)
PAYDIREKT_API_KEY = getattr(settings, 'PAYDIREKT_API_KEY', False)

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

if getattr(settings, 'PAYDIREKT', False):
    PAYDIREKT_ROOT_URL = settings.PAYDIREKT_ROOT_URL
