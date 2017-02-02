import json

from django.conf import settings
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from .models import PaydirektCheckout, PaydirektWrapper, PaydirektCapture


class NotifyPaydirektView(View):
    paydirekt_wrapper = PaydirektWrapper(auth={
                            'API_SECRET': settings.PAYDIREKT_API_SECRET,
                            'API_KEY': settings.PAYDIREKT_API_KEY,
                        })

    def post(self, request, *args, **kwargs):
        request_data = json.loads(request.body)
        checkout_id = request_data['checkoutId']
        reference_number = request_data['merchantOrderReferenceNumber']

        if 'transactionId' in request_data:
            transaction_id = request_data['transactionId']
            capture_status = request_data['captureStatus']
            try:
                PaydirektCheckout.objects.get(checkout_id=checkout_id)
            except PaydirektCheckout.DoesNotExist:
                return HttpResponse(status=400)
            try:
                paydirekt_capture = PaydirektCapture.objects.get(transaction_id=transaction_id)
            except PaydirektCapture.DoesNotExist:
                return HttpResponse(status=400)
            return self.handle_updated_capture(paydirekt_checkout=paydirekt_capture, expected_status=capture_status)
        else:
            checkout_status = request_data['checkoutStatus']
            try:
                paydirekt_checkout = PaydirektCheckout.objects.get(checkout_id=checkout_id)
            except PaydirektCheckout.DoesNotExist:
                return HttpResponse(status=400)
            return self.handle_updated_checkout(paydirekt_checkout=paydirekt_checkout, expected_status=checkout_status)

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(NotifyPaydirektView, self).dispatch(request, *args, **kwargs)

    def handle_updated_checkout(self, paydirekt_checkout, expected_status=None):
        """
            Override to use the paydirekt_checkout in the way you want.
        """
        updated_checkout = self.paydirekt_wrapper.update_checkout(paydirekt_checkout, expected_status=expected_status)
        if updated_checkout:
            if updated_checkout.status not in settings.PAYDIREKT_VALID_CHECKOUT_STATUS:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(_('Paydirekt: Status of checkout {} is now {}').format(updated_checkout.checkout_id, updated_checkout.status))
            return HttpResponse(status=200)
        return HttpResponse(status=400)

    def handle_updated_capture(self, paydirekt_checkout, expected_status=None):
        """
            Override to use the paydirekt_capture in the way you want.
        """
        updated_capture = self.paydirekt_wrapper.update_checkout(paydirekt_checkout, expected_status=expected_status)
        if updated_capture:
            if updated_capture.status not in settings.PAYDIREKT_VALID_CAPTURE_STATUS:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(_('Paydirekt: Status of capture {} is now {}').format(updated_capture.checkout_id, updated_capture.status))
            return HttpResponse(status=200)
        return HttpResponse(status=400)
