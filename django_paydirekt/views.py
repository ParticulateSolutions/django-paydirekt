import json

from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from .wrappers import PaydirektWrapper
from .models import PaydirektCapture, PaydirektCheckout
from django_paydirekt import settings as django_paydirekt_settings


class NotifyPaydirektView(View):
    paydirekt_wrapper = PaydirektWrapper(auth={
        'API_SECRET': django_paydirekt_settings.PAYDIREKT_API_SECRET,
        'API_KEY': django_paydirekt_settings.PAYDIREKT_API_KEY,
    })

    def post(self, request, *args, **kwargs):
        request_data = json.loads(request.body)

        # general attributes
        if 'checkoutId' not in request_data:
            return HttpResponse(status=400)
        checkout_id = request_data['checkoutId']

        if 'merchantOrderReferenceNumber' not in request_data:
            return HttpResponse(status=400)
        reference_number = request_data['merchantOrderReferenceNumber']

        # capture attributes
        if 'transactionId' in request_data:
            transaction_id = request_data['transactionId']
            if 'captureStatus' not in request_data:
                return HttpResponse(status=400)
            capture_status = request_data['captureStatus']
            try:
                PaydirektCheckout.objects.get(checkout_id=checkout_id)
            except PaydirektCheckout.DoesNotExist:
                return HttpResponse(status=400)
            try:
                paydirekt_capture = PaydirektCapture.objects.get(transaction_id=transaction_id)
            except PaydirektCapture.DoesNotExist:
                return HttpResponse(status=400)
            return self.handle_updated_capture(paydirekt_capture=paydirekt_capture, expected_status=capture_status)

        # express checkout attributes
        elif 'destinations' in request_data:
            if 'orderAmount' not in request_data:
                return HttpResponse(status=400)
            for destination in request_data['destinations']:
                if 'id' not in destination:
                    return HttpResponse(status=400)
                if 'countryCode' not in destination:
                    return HttpResponse(status=400)
                if 'zip' not in destination:
                    return HttpResponse(status=400)
                if 'dhlPackstation' not in destination:
                    return HttpResponse(status=400)
            try:
                paydirekt_checkout = PaydirektCheckout.objects.get(checkout_id=checkout_id)
            except PaydirektCheckout.DoesNotExist:
                return HttpResponse(status=400)
            self.check_destinations(paydirekt_checkout, request_data, request)

        # normal checkout attributes
        else:
            if 'checkoutStatus' not in request_data:
                return HttpResponse(status=400)
            checkout_status = request_data['checkoutStatus']
            try:
                paydirekt_checkout = PaydirektCheckout.objects.get(checkout_id=checkout_id)
            except PaydirektCheckout.DoesNotExist:
                return HttpResponse(status=400)
            return self.handle_updated_checkout(paydirekt_checkout=paydirekt_checkout, expected_status=checkout_status)

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(NotifyPaydirektView, self).dispatch(request, *args, **kwargs)

    def check_destinations(self, paydirekt_checkout, request_data, request):
        """
            Override to check destinations in the way you want.
        """
        links = {'self': {'href': request.path}}
        checked_destinations = []
        for destination in request_data['destinations']:
            id = destination['id']
            country_code = destination['countryCode']
            zip = destination['zip']
            dhl_packstation = destination['dhlPackstation']

            zip_valid = False
            for zip_code in django_paydirekt_settings.PAYDIREKT_VALID_ZIP_CODES:
                if '*' in zip_code:
                    if zip.startsWith(zip_code.split('*')[0]):
                        zip_valid = True
                else:
                    if zip == zip_code:
                        zip_valid = True
            if country_code in django_paydirekt_settings.PAYDIREKT_VALID_COUNTRY_CODES and zip_valid and \
               (not dhl_packstation or django_paydirekt_settings.PAYDIREKT_VALID_PACKSTATION):
                if dhl_packstation:
                    valid_billing_destination = False
                else:
                    valid_billing_destination = True
                valid_shipping_destination = True
                shipping_options = django_paydirekt_settings.PAYDIREKT_SHIPPING_OPTIONS
            else:
                valid_billing_destination = False
                valid_shipping_destination = False
                shipping_options = []
            checked_destinations.append({'id': id,
                                         'countryCode': country_code,
                                         'zip': zip,
                                         'dhl_packstation': dhl_packstation,
                                         'validBillingDestination': valid_billing_destination,
                                         'validShippingDestination': valid_shipping_destination,
                                         'shippingOptions': shipping_options})
        return HttpResponse({'checkedDestinations': checked_destinations, '_links': links}, status=200, content_type='application/hal+json;charset=UTF-8')

    def handle_updated_checkout(self, paydirekt_checkout, expected_status=None):
        """
            Override to use the paydirekt_checkout in the way you want.
        """
        updated_checkout = paydirekt_checkout
        if updated_checkout.refresh_from_paydirekt(self.paydirekt_wrapper, expected_status=expected_status):
            if updated_checkout.status not in django_paydirekt_settings.PAYDIREKT_VALID_CHECKOUT_STATUS:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(_('Paydirekt: Status of checkout {} is now {}').format(updated_checkout.checkout_id, updated_checkout.status))
                return HttpResponse(status=400)
            return HttpResponse(status=200)
        return HttpResponse(status=400)

    def handle_updated_capture(self, paydirekt_capture, expected_status=None):
        """
            Override to use the paydirekt_capture in the way you want.
        """
        updated_capture = paydirekt_capture
        if updated_capture.refresh_from_paydirekt(self.paydirekt_wrapper, expected_status=expected_status):
            if updated_capture.status not in django_paydirekt_settings.PAYDIREKT_VALID_CAPTURE_STATUS:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(_('Paydirekt: Status of capture {} is now {}').format(updated_capture.checkout_id, updated_capture.status))
                return HttpResponse(status=400)
            return HttpResponse(status=200)
        return HttpResponse(status=400)
