from __future__ import unicode_literals

import logging

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django_paydirekt.utils import build_paydirekt_full_uri


@python_2_unicode_compatible
class PaydirektCheckout(models.Model):
    checkout_id = models.CharField(_("checkout id"), max_length=255, unique=True)
    payment_type = models.CharField(_("payment type"), max_length=255)
    total_amount = models.DecimalField(_("total amount"), max_digits=9, decimal_places=2)
    status = models.CharField(_("status"), max_length=255, blank=True)
    link = models.URLField(_("link"))
    approve_link = models.URLField(_("approve link"))
    close_link = models.URLField(_("close link"), blank=True)
    captures_link = models.URLField(_("captures link"), blank=True)
    refunds_link = models.URLField(_("refunds link"), blank=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    last_modified = models.DateTimeField(_("last modified"), auto_now=True)

    objects = models.Manager()

    def __str__(self):
        return self.checkout_id

    class Meta:
        verbose_name = _("Paydirekt Checkout")
        verbose_name_plural = _("Paydirekt Checkouts")

    def create_capture(self,
                       amount,
                       paydirekt_wrapper,
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

        capture_response = paydirekt_wrapper.call_api(url=self.captures_link, data=capture_data)

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

    def create_refund(self,
                       amount,
                       paydirekt_wrapper,
                       note=None,
                       reason=None,
                       reference_number=None,
                       reconciliation_reference_number=None):
        if not self.refunds_link:
            return False
        refund_data = {
            'amount': amount,
        }
        if reason:
            refund_data.update({'reason': reason})
        if note:
            refund_data.update({'note': note})
        if reference_number:
            refund_data.update({'merchantRefundReferenceNumber': reference_number})
        if reconciliation_reference_number:
            refund_data.update({'merchantReconciliationReferenceNumber': reconciliation_reference_number})

        refund_response = paydirekt_wrapper.call_api(url=self.refunds_link, data=refund_data)

        if refund_response and 'amount' in refund_response and refund_response['amount'] == float(amount):
            return PaydirektRefund.objects.create(
                checkout=self,
                amount=amount,
                transaction_id=refund_response['transactionId'],
                status=refund_response['status'],
                link=refund_response['_links']['self']['href'],
                refund_type=refund_response['type']
            )
        else:
            return False

    def close(self, paydirekt_wrapper):
        if not self.close_link:
            return False
        close_response = paydirekt_wrapper.call_api(url=self.close_link, data='')
        if close_response and 'status' in close_response and close_response['status'] == 'CLOSED':
            self.status = 'CLOSED'
            self.save()
            return True
        return False

    def refresh_from_paydirekt(self, paydirekt_wrapper, expected_status=None):
        checkout_response = paydirekt_wrapper.call_api(url=self.link)
        if not checkout_response:
            logger = logging.getLogger(__name__)
            logger.error("Paydirekt Checkout Link not available: {}".format(self.link))
            return False

        if expected_status and expected_status != checkout_response['status']:
            logger = logging.getLogger(__name__)
            logger.error("Paydirekt Checkout Status Error: expected: {0}, found: {1}".format(expected_status, checkout_response['status']))
            return False

        self.status = checkout_response['status']

        if '_links' in checkout_response:
            if 'close' in checkout_response['_links']:
                self.close_link = checkout_response['_links']['close']['href']
            if 'captures' in checkout_response['_links']:
                self.captures_link = checkout_response['_links']['captures']['href']
            if 'refunds' in checkout_response['_links']:
                self.refunds_link = checkout_response['_links']['refunds']['href']
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
        verbose_name = _("Paydirekt Capture")
        verbose_name_plural = _("Paydirekt Captures")

    def refresh_from_paydirekt(self, paydirekt_wrapper, expected_status=None):
        capture_response = paydirekt_wrapper.call_api(url=self.link)
        if not capture_response:
            logger = logging.getLogger(__name__)
            logger.error("Paydirekt Capture Link not available: {}".format(self.link))
            return False

        if expected_status and expected_status != capture_response['status']:
            logger = logging.getLogger(__name__)
            logger.error("Paydirekt Capture Status Error: expected: {0}, found: {1}".format(expected_status, capture_response['status']))
            return False

        self.status = capture_response['status']
        self.save()

        return True


@python_2_unicode_compatible
class PaydirektRefund(models.Model):
    checkout = models.ForeignKey(PaydirektCheckout, verbose_name=_("checkout"), related_name='refunds')
    amount = models.DecimalField(_("amount"), max_digits=9, decimal_places=2)
    transaction_id = models.CharField(_("transaction id"), max_length=255, unique=True)
    link = models.URLField(_("link"))
    status = models.CharField(_("status"), max_length=255, blank=True)
    refund_type = models.CharField(_("refund type"), max_length=255, blank=True)

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    last_modified = models.DateTimeField(_("last modified"), auto_now=True)

    objects = models.Manager()

    def __str__(self):
        return self.transaction_id

    class Meta:
        verbose_name = _("Paydirekt Refund")
        verbose_name_plural = _("Paydirekt Refund")

    def refresh_from_paydirekt(self, paydirekt_wrapper, expected_status=None):
        refund_response = paydirekt_wrapper.call_api(url=self.link)
        if not refund_response:
            logger = logging.getLogger(__name__)
            logger.error("Paydirekt Refund Link not available: {}".format(self.link))
            return False

        if expected_status and expected_status != refund_response['status']:
            logger = logging.getLogger(__name__)
            logger.error("Paydirekt Refund Status Error: expected: {0}, found: {1}".format(expected_status, refund_response['status']))
            return False

        self.status = refund_response['status']
        self.save()

        return True
