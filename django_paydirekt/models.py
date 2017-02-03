from __future__ import unicode_literals

import logging

from django.contrib.sites.models import Site
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django_paydirekt.utils import build_paydirekt_full_uri


@python_2_unicode_compatible
class PaydirektCheckout(models.Model):
    checkout_id = models.CharField(_("checkout id"), max_length=255, unique=True)
    payment_type = models.CharField(_("payment type"), max_length=255, unique=True)
    total_amount = models.DecimalField(_("total amount"), max_digits=9, decimal_places=2)
    status = models.CharField(_("status"), max_length=255, blank=True)
    link = models.URLField(_("link"))
    approve_link = models.URLField(_("approve link"))
    close_link = models.URLField(_("close link"), blank=True)
    captures_link = models.URLField(_("captures link"), blank=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    last_modified = models.DateTimeField(_("last modified"), auto_now=True)

    objects = models.Manager()

    def __str__(self):
        return self.checkout_id

    class Meta:
        verbose_name = _("Paydirekt checkout")
        verbose_name_plural = _("Paydirekt checkouts")

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
            notification_url = build_paydirekt_full_uri(notification_url)
            capture_data.update({'callbackUrlStatusUpdates': notification_url})
        if delivery_information:
            capture_data.update({'deliveryInformation': delivery_information})

        capture_response = wrapper.call_api(url=self.captures_link, data=capture_data)

        if capture_response and 'amount' in capture_response and capture_response['amount'] == float(amount):
            return PaydirektCapture.objects.create(
                checkout=self,
                amount=amount,
                final=final,
                transaction_id=capture_response['transactionId'],
                status=capture_response['status'],
                link=capture_response['_links']['self']['href'],
                capture_type=capture_response['type']
            )
        else:
            return False

    def refresh_from_paydirekt(self, wrapper, expected_status=None):
        checkout_response = wrapper.call_api(url=self.link)
        if not checkout_response:
            logger = logging.getLogger(__name__)
            logger.error("Paydirekt Checkout Link not available: {}".format(self.link))
            return False

        if expected_status and expected_status != checkout_response['status']:
            logger = logging.getLogger(__name__)
            logger.error("Paydirekt Checkout Status Error: expected: {0}, found: {1}".format(expected_status, checkout_response['status']))
            return False

        self.status = checkout_response['status']

        if self.payment_type == 'ORDER' and self.status == 'APPROVED':
            self.close_link = checkout_response['_links']['close']['href']
            self.captures_link = checkout_response['_links']['captures']['href']
        self.save()

        return True


@python_2_unicode_compatible
class PaydirektCapture(models.Model):
    checkout = models.ForeignKey(PaydirektCheckout, verbose_name=_("checkout"), related_name='captures')
    amount = models.DecimalField(_("amount"), max_digits=9, decimal_places=2)
    transaction_id = models.CharField(_("transaction id"), max_length=255, unique=True)
    final = models.BooleanField(_("final"), default=False)
    link = models.URLField(_("link"))
    status = models.CharField(_("status"), max_length=255, blank=True)
    capture_type = models.CharField(_("capture type"), max_length=255, blank=True)

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    last_modified = models.DateTimeField(_("last modified"), auto_now=True)

    objects = models.Manager()

    def __str__(self):
        return self.transaction_id

    class Meta:
        verbose_name = _("Paydirekt checkout")
        verbose_name_plural = _("Paydirekt checkouts")

    def refresh_from_paydirekt(self, wrapper, expected_status=None):
        checkout_response = wrapper.call_api(url=self.link)
        if not checkout_response:
            logger = logging.getLogger(__name__)
            logger.error("Paydirekt Capture Link not available: {}".format(self.link))
            return False

        if expected_status and expected_status != checkout_response['status']:
            logger = logging.getLogger(__name__)
            logger.error("Paydirekt Capture Status Error: expected: {0}, found: {1}".format(expected_status, checkout_response['status']))
            return False

        self.status = checkout_response['status']
        self.save()

        return True
