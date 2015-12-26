from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from .factories import TestModelFactory


class TransactionTests(APITestCase):

    def test_create_outgoing_transactions(self):
        """
        Assert we can create a new outgoing transaction object.
        """
        test_model = TestModelFactory()
        outgoing_transaction = test_model.to_outgoing('I')
        url = reverse('outgoing-transaction-list')
        data = {
            'tx': outgoing_transaction.tx.decode(),
            'tx_name': outgoing_transaction.tx_name,
            'tx_pk': str(outgoing_transaction.tx_pk),
            'producer': outgoing_transaction.producer,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, data)

    def test_post_incoming_transactions(self):
        """
        Assert we can create a new outgoing transaction object.
        """
        test_model = TestModelFactory()
        outgoing_transaction = test_model.to_outgoing('I')
        url = reverse('incoming-transaction-list')
        data = {
            'tx': outgoing_transaction.tx.decode(),
            'tx_name': outgoing_transaction.tx_name,
            'tx_pk': str(outgoing_transaction.tx_pk),
            'producer': outgoing_transaction.producer,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, data)
