from django.test import TestCase

from ..classes import Consumer
from ..models import OutgoingTransaction, IncomingTransaction


class TestPlayTransactions(TestCase):

    multi_db = True

    def setUp(self):
        pass

    def test_playing_transactions(self):
        self.copy_db_to_db()
        Consumer('test_server').consume()
        self.assertEqual(IncomingTransaction.objects.using('test_server').filter(is_consumed=False).count(), 0)

    def copy_db_to_db(self):
        OutgoingTransaction.objects.using('default').all().copy_to_incoming_transaction('test_server')
        self.assertEquals(
            OutgoingTransaction.objects.using('default').all().count(),
            IncomingTransaction.objects.using('test_server').all().count())

    def populate_default_outgoing(self):
        """Override in application subclass to populate outgoing transactions for a real life simulation
        of playing transactions"""
        pass
