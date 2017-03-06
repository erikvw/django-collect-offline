import os

from django.test.testcases import TestCase
from django.test.utils import tag

from edc_example.models import TestModel

from ..models import OutgoingTransaction
from ..utils.transaction_tx_pk import previous_tx_pk_and_next_tx_pk


@tag('TestTransactionOrder')
class TestTransactionOrder(TestCase):

    def setUp(self):
        TestCase.setUp(self)

    @tag('test_current_tx_pk')
    def test_current_tx_pk(self):
        #  Create transactions
        TestModel.objects.using('client').create(f1='erik')
        TestModel.objects.using('client').create(f1='setsiba')

        previous_tx_pk, next_tx_pk = previous_tx_pk_and_next_tx_pk(using='client')

        # Dump transactions
        OutgoingTransaction.objects.using('client').filter(
            is_consumed_server=False).update(
            current_tx_pk=next_tx_pk,
            previous_tx_pk=previous_tx_pk,
            is_consumed_server=True)

        outgoing = OutgoingTransaction.objects.using('client').filter(
            current_tx_pk=next_tx_pk).first()

        self.assertEqual(
            outgoing.previous_tx_pk,
            outgoing.current_tx_pk)

    @tag('test_current_tx_pk1')
    def test_current_tx_pk1(self):
        #  Create transactions
        TestModel.objects.using('client').create(f1='erik10')
        TestModel.objects.using('client').create(f1='setsiba10')

        previous_tx_pk, next_tx_pk = previous_tx_pk_and_next_tx_pk(using='client')
        # Dump transactions
        OutgoingTransaction.objects.using('client').filter(
            is_consumed_server=False).update(
            current_tx_pk=next_tx_pk,
            previous_tx_pk=previous_tx_pk,
            is_consumed_server=True)

        # Create another transactions
        TestModel.objects.using('client').create(f1='erik1')
        TestModel.objects.using('client').create(f1='setsiba1')

        previous_tx_pk, next_tx_pk = previous_tx_pk_and_next_tx_pk(using='client')
        self.assertTrue(previous_tx_pk)
        self.assertTrue(next_tx_pk)

        tx_to_dump_count = OutgoingTransaction.objects.using('client').filter(
            is_consumed_server=False).count()
        self.assertGreater(tx_to_dump_count, 0)

        OutgoingTransaction.objects.using('client').filter(
            is_consumed_server=False).update(
            current_tx_pk=next_tx_pk,
            previous_tx_pk=previous_tx_pk,
            is_consumed_server=True)

        outgoing = OutgoingTransaction.objects.using('client').filter(
            current_tx_pk=next_tx_pk).first()

        self.assertNotEqual(
            outgoing.previous_tx_pk,
            outgoing.current_tx_pk)
