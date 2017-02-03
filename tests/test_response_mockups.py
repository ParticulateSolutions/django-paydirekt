#!/usr/bin/env python
# -*- coding: utf-8 -*-

TEST_RESPONSES = {
    'token_obtain': {
         'access_token': 'NM_eSvBjAI9lYZKpVFlsPZ0uV7B_e5RIgelb85i6NYVFVQNTEESoI8vJAB6m-2-T12h8zl6aiMxPEjQ6aJhQS2eBeDuJ0ePAUI6RAYsdl4Ju-vr0kouqY-pgwaZz9wrDkCsEfPDDMvneNZNzQoKFxI0zOKF2nExMJsQ5DQiWDW8nfWfWTBP6Rk5vISrcbvXYwI0uKEJALSlyz_7XhDC7n8BBn1Jf0FIDfkGZPJgax_WxOyCAC2VCeyJs4lZLZ3ctKnLSIB__4tuxB5__s7n4lVV8IFbAYmdpJNgRNRtsQ2e6_d4zOzA84jgW8QluEwjHNSMnqRJnHnDG8YX-NgDFZ2-3D87qQdR_jclce13o5wrEBabdGXX1sj81jKfQlnPohS179x09pBQU1JHIyKxVUDuZTx-aUNFOuWBCjGJ7vBKmcqHmLQffIUQSMia2oIfjQNHhdGxWtVDAFohRV-mynTvn49rwn1SaubTGxio73P3rZwoyrgIy8kdXKwU622kPo24q4Zi8qNvBhYPTF4gq5apck5CPEFVGp5GuP_Efzn1Y7z5LuNF-2yNsRCFka1F45puZ3BNnl_0Oluqlm1NE_1Xm8g2FuxLAIfrTYvteyQmT-KCRXk_3lrIbsJBkKWGR35MXI0ykYVXiZCMIgQ048xaIxZqTejoR37dfLL778hJnCweWObREZpt1fKKFYTpQVYxEo2NQuUSt23xfyc-HjdHY360k3UBQMahz4Pb3j8vmGAALKtGEbWquf_-zjh3urM5RXR6sGB0xQERV_V8uU9AWcaDbbvGR-_sni1ryr9LUUkwnax7XR-0zPOhQaJuOYoeempeYGBkA9RlPzEB1aSj6IIGIeb81C0cTHkfBBKRXZ3VkRDd0doRwdDCaU44cRPKtbv8qv-j4eJgBry3_wxwTYutYk4Yrpd3bTrON0wMTuPqnqk627kqyG8y010Ye56HZfB9uwZC4fBo5YEkeyOfy55BsPePjLbuoQmqGpvFLHyv5l4wM6J0eWSXsS7S-th5VvIGI3ZP4671aMg3XAg2P0jsqBDSv1ZqLWKGhN-q09FNJw6_qjP-ulRzuW5jpxKhrSnQqVpOAlaiMkr7IljfBvGTWClrIH23zF-HGobHePMnvs40TdKJ7tKXSDQw0ZayYXrcpFP1Tpl82MZX5jMaxcYVSJ5MbkVT70w4FBFlOnnYDB39_A7j3WJIxMrtI2xthJEk-4QirCSFKTEvDZbOhRJ7gy9MyEEv-uePqKAg',
         'token_type': 'bearer',
         'expires_in': 3599,
         'scope': 'checkout',
         'jti': 'be653156-d9cc-4950-aed3-949dc2e20c3f'
    },
    'status_approved': {
         'status': 'APPROVED',
         'type': 'DIRECT_SALE',
         'totalAmount': 100.0,
         'shippingAmount': 3.5,
         'orderAmount': 96.5,
         'items': [
             {
                 'quantity': 3,
                 'name': 'Bobbycar',
                 'ean': '800001303',
                 'price': 25.99
             },
             {
                 'quantity': 1,
                 'name': 'Helm',
                 'price': 18.53
             }
         ],
         'currency': 'EUR',
         'overcapture': False,
         'shippingAddress': {
             'addresseeGivenName': 'Marie',
             'addresseeLastName': 'Mustermann',
             'street': 'Packstation',
             'streetNr': '999',
             'additionalAddressInformation': '1234567890',
             'zip': '90402',
             'city': 'Schwaig',
             'countryCode': 'DE'
         },
         'deliveryInformation': {
             'expectedShippingDate': '2016-10-19T12:00:00Z',
             'logisticsProvider': 'DHL',
             'trackingNumber': '1234567890'
         },
         'merchantCustomerNumber': 'cust-732477',
         'merchantOrderReferenceNumber': 'order-A12223412',
         'merchantReconciliationReferenceNumber': 'recon-A12223412',
         'merchantInvoiceReferenceNumber': '20150112334345',
         'note': 'Ihr Einkauf bei Spielauto-Versand.',
         'sha256hashedEmailAddress': 'fxP4R-IxH1Eaxpb0f_i5Shc8-FrYrtmx5lx35f9Xzgg',
         'minimumAge': 18,
         'redirectUrlAfterSuccess': 'https://spielauto-versand.de/order/123/success',
         'redirectUrlAfterCancellation': 'https://spielauto-versand.de/order/123/cancellation',
         'redirectUrlAfterAgeVerificationFailure': 'https://spielauto-versand.de/order/123/ageverificationfailed',
         'redirectUrlAfterRejection': 'https://spielauto-versand.de/order/123/rejection',
         'callbackUrlStatusUpdates': 'https://spielauto-versand.de/callback/status'
    },
    'status_expired': {
         'status': 'EXPIRED',
         'type': 'DIRECT_SALE',
         'totalAmount': 100.0,
         'shippingAmount': 3.5,
         'orderAmount': 96.5,
         'items': [
             {
                 'quantity': 3,
                 'name': 'Bobbycar',
                 'ean': '800001303',
                 'price': 25.99
             },
             {
                 'quantity': 1,
                 'name': 'Helm',
                 'price': 18.53
             }
         ],
         'currency': 'EUR',
         'overcapture': False,
         'shippingAddress': {
             'addresseeGivenName': 'Marie',
             'addresseeLastName': 'Mustermann',
             'street': 'Packstation',
             'streetNr': '999',
             'additionalAddressInformation': '1234567890',
             'zip': '90402',
             'city': 'Schwaig',
             'countryCode': 'DE'
         },
         'deliveryInformation': {
             'expectedShippingDate': '2016-10-19T12:00:00Z',
             'logisticsProvider': 'DHL',
             'trackingNumber': '1234567890'
         },
         'merchantCustomerNumber': 'cust-732477',
         'merchantOrderReferenceNumber': 'order-A12223412',
         'merchantReconciliationReferenceNumber': 'recon-A12223412',
         'merchantInvoiceReferenceNumber': '20150112334345',
         'note': 'Ihr Einkauf bei Spielauto-Versand.',
         'sha256hashedEmailAddress': 'fxP4R-IxH1Eaxpb0f_i5Shc8-FrYrtmx5lx35f9Xzgg',
         'minimumAge': 18,
         'redirectUrlAfterSuccess': 'https://spielauto-versand.de/order/123/success',
         'redirectUrlAfterCancellation': 'https://spielauto-versand.de/order/123/cancellation',
         'redirectUrlAfterAgeVerificationFailure': 'https://spielauto-versand.de/order/123/ageverificationfailed',
         'redirectUrlAfterRejection': 'https://spielauto-versand.de/order/123/rejection',
         'callbackUrlStatusUpdates': 'https://spielauto-versand.de/callback/status'
    },
    'minimal_status_approved': {
        'status': 'APPROVED',
        'type': 'DIRECT_SALE',
        'totalAmount': 14.00,
        'currency': 'EUR',
        'shippingAddress': {
            'addresseeGivenName': 'Hermann',
            'addresseeLastName': 'Meyer',
            'street': 'Wieseneckstraße',
            'streetNr': '26',
            'zip': '90571',
            'city': 'Schwaig bei Nürnberg',
            'countryCode': 'DE'
        },
        'merchantOrderReferenceNumber': 'order-A12223412',
        'redirectUrlAfterSuccess': 'https://spielauto-versand.de/order/123/success',
        'redirectUrlAfterCancellation': 'https://spielauto-versand.de/order/123/cancellation',
        'redirectUrlAfterRejection': 'https://spielauto-versand.de/order/123/rejection'
    },
}
