import json

from django.db.utils import IntegrityError
from django.test.testcases import TestCase
from django.db import transaction

from ..classes import Consumer
from ..models import IncomingTransaction, OutgoingTransaction

from .models import TestModel


class TestTx(TestCase):

    def test_json(self):
        """Assert returns a valid json object."""
        test_model = TestModel(character='erik', integer=1)
        test_model.use_encryption = False
        self.assertTrue(json.loads(test_model.to_json()))

    def test_encrypted_json1(self):
        """Assert cannot json.load bytes (encrypted json)."""
        test_model = TestModel(character='erik', integer=1)
        self.assertRaises(TypeError, json.loads, test_model.to_json())

    def test_save_to_outgoing(self):
        """Assert can json.load decrypted json (roundtrip)."""
        test_model = TestModel.objects.create(character='erik', integer=1)
        with transaction.atomic():
            self.assertTrue(test_model.to_outgoing('I'))

    def test_fetch_incoming(self):
        """Asserts model instance to outgoing and fetched by incoming."""
        test_model = TestModel(character='erik', integer=1)
        with transaction.atomic():
            test_model.save()
        outgoing = test_model.to_outgoing('I')
        consumer = Consumer(allow_from_self=True)
        consumer.fetch_outgoing(None, None)
        self.assertTrue(IncomingTransaction.objects.get(tx_pk=outgoing.tx_pk))
        self.assertTrue(OutgoingTransaction.objects.get(tx_pk=outgoing.tx_pk).is_consumed)

    def test_save_to_model(self):
        test_model = TestModel.objects.create(character='erik', integer=1)
        pk = test_model.pk
        with transaction.atomic():
            test_model.save()
        outgoing = test_model.to_outgoing('I')
        consumer = Consumer(allow_from_self=True)
        consumer.fetch_outgoing(None, 'destination')
        incoming = IncomingTransaction.objects.using('destination').get(tx_pk=outgoing.tx_pk)
        self.assertTrue(incoming.to_model_instance(to='destination'))
        self.assertTrue(TestModel.objects.using('destination').get(pk=pk))

    def test_save_duplicate(self):
        test_model = TestModel.objects.create(character='erik', integer=1)
        pk = test_model.pk
        with transaction.atomic():
            test_model.save()
        outgoing = test_model.to_outgoing('I')
        consumer = Consumer(allow_from_self=True)
        consumer.fetch_outgoing(None, 'destination')
        incoming = IncomingTransaction.objects.using('destination').get(tx_pk=outgoing.tx_pk)
        incoming.to_model_instance(to='destination')
        TestModel.objects.using('destination').get(pk=pk)
        self.assertTrue(incoming.is_consumed)
        incoming.is_consumed = False
        incoming.save(using='destination')
        self.assertFalse(incoming.is_consumed)
        incoming.to_model_instance(to='destination')
