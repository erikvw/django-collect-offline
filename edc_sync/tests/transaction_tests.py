from django.test import TestCase

from edc.device.sync.classes import Consumer, DeserializeFromTransaction, SerializeToTransaction
from edc.device.sync.models import Producer, OutgoingTransaction, IncomingTransaction, TestItem


class TransactionTests(TestCase):

    def setUp(self):
        self.producer = None
        self.using_destination = 'dispatch_destination'
        self.using_source = 'default'
        Producer.objects.using(self.using_source).delete()
        OutgoingTransaction.objects.using(self.using_destination).delete()
        IncomingTransaction.objects.using(self.using_source).delete()

    def create_producer(self, is_active=False):
        # add a in_active producer
        self.producer = Producer.objects.create(name='test_producer', settings_key=self.using_destination, is_active=is_active)

    def create_test_item(self, identifier, using=None):
        return TestItem.objects.using(using).create(test_item_identifier=identifier, comment='TEST_COMMENT')

    def test_transactions_p1(self):
        """Confirm outgoing transactions are created according to the \'using\'."""
        TestItem.objects.all().delete()
        TestItem.objects.using(self.using_destination).all().delete()
        OutgoingTransaction.objects.all().delete()
        OutgoingTransaction.objects.using(self.using_destination).all().delete()
        IncomingTransaction.objects.all().delete()
        IncomingTransaction.objects.using(self.using_source).all().delete()
        Producer.objects.using(self.using_source).delete()
        self.create_producer()
        # create a test item on source
        src_item = self.create_test_item('SRC_IDENTIFIER', self.using_source)
        # assert outgoing transactions on source
        self.assertEqual(OutgoingTransaction.objects.using(self.using_source).filter(tx_name=src_item._meta.object_name, tx_pk=src_item.pk).count(), 1)
        # assert NO outgoing transactions on destination
        self.assertEqual(OutgoingTransaction.objects.using(self.using_destination).filter(tx_name=src_item._meta.object_name, tx_pk=src_item.pk).count(), 0)
        # create a test item on using_destination
        dst_item = self.create_test_item('DST_IDENTIFIER', self.using_destination)
        # assert NO outgoing transactions on source
        self.assertEqual(OutgoingTransaction.objects.filter(tx_name=dst_item._meta.object_name, tx_pk=dst_item.pk).count(), 0)
        # assert outgoing transactions on destination
        self.assertEqual(OutgoingTransaction.objects.using(self.using_destination).filter(tx_name=dst_item._meta.object_name, tx_pk=dst_item.pk).count(), 1)

    def test_transactions_p2(self):
        TestItem.objects.all().delete()
        TestItem.objects.using(self.using_destination).all().delete()
        OutgoingTransaction.objects.all().delete()
        OutgoingTransaction.objects.using(self.using_destination).all().delete()
        IncomingTransaction.objects.all().delete()
        IncomingTransaction.objects.using(self.using_source).all().delete()
        Producer.objects.using(self.using_source).delete()
        self.create_producer()
        # create a test item on source
        src_item = self.create_test_item('SRC_IDENTIFIER', self.using_source)
        # assert value of comment which will be changed later
        self.assertEqual(src_item.comment, 'TEST_COMMENT')
        # assert a outgoing transaction was created on source
        self.assertEqual(OutgoingTransaction.objects.using(self.using_source).filter(tx_name=src_item._meta.object_name, is_consumed=False).count(), 1)
        # assert no Incoming on destination
        self.assertEqual(IncomingTransaction.objects.using(self.using_destination).filter(tx_name=src_item._meta.object_name).count(), 0)
        # create a consumer on the destination to fetch outgoing on source
        self.assertEqual(TestItem.objects.using(self.using_destination).all().count(), 0)
        consumer = Consumer(using=self.using_destination)
        consumer.fetch_outgoing(self.using_source)
        # assert a outgoing transaction was consumed on source
        self.assertEqual(OutgoingTransaction.objects.using(self.using_source).filter(tx_name=src_item._meta.object_name, is_consumed=True).count(), 1)
        # ... and an incoming transactions was created on destination
        self.assertEqual(IncomingTransaction.objects.using(self.using_destination).filter(tx_name=src_item._meta.object_name).count(), 1)
        # ... assert the incoming transactions are not consumed
        self.assertEqual(IncomingTransaction.objects.using(self.using_destination).filter(tx_name=src_item._meta.object_name, is_consumed=False).count(), 1)
        # consume on destination
        consumer = Consumer(using=self.using_destination)
        # assert consumer is looking at destination
        self.assertEqual(consumer.get_using(), self.using_destination)
        # consume on destination
        consumer.consume(check_hostname=False)
        # assert the TestItem is now on destination
        self.assertEqual(TestItem.objects.using(self.using_destination).all().count(), 1)
        # get the TestItem on destination and change
        dst_item = TestItem.objects.using(self.using_destination).get(test_item_identifier='SRC_IDENTIFIER')
        # ... from this ...
        self.assertEqual(dst_item.comment, 'TEST_COMMENT')
        # ... to this...
        dst_item.comment = 'HELLO FROM DST'
        # save TestItem on destination
        dst_item.save(using=self.using_destination)
        # assert comment has changed on destination
        dst_item = TestItem.objects.using(self.using_destination).get(test_item_identifier='SRC_IDENTIFIER')
        self.assertEqual(dst_item.comment, 'HELLO FROM DST')
        # assert there is an outgoing transaction on destination
        self.assertEqual(OutgoingTransaction.objects.using(self.using_destination).filter(tx_name=dst_item._meta.object_name, is_consumed=False).count(), 1)
        # create a consumer on source
        consumer = Consumer(using=self.using_source)
        self.assertEqual(consumer.get_using(), self.using_source)
        # fetch the outgoing from destination
        consumer.fetch_outgoing(self.using_destination)
        # assert a outgoing transaction was consumed on destination
        self.assertEqual(OutgoingTransaction.objects.using(self.using_destination).filter(tx_name=src_item._meta.object_name, is_consumed=True).count(), 1)
        # ... and an incoming transactions was created on source
        self.assertEqual(IncomingTransaction.objects.using(self.using_source).filter(tx_name=src_item._meta.object_name).count(), 1)
        # ... assert the incoming transactions are not consumed
        self.assertEqual(IncomingTransaction.objects.using(self.using_source).filter(tx_name=src_item._meta.object_name, is_consumed=False).count(), 1)
        # consume incoming on source
        consumer.consume(check_hostname=False)
        # verify updated
        src_item = TestItem.objects.get(test_item_identifier='SRC_IDENTIFIER')
        self.assertEqual(src_item.comment, 'HELLO FROM DST')

    def test_transactions_p3(self):
        """Checks that those that inherit from Base correctly report the \'using\' argument."""
        TestItem.objects.all().delete()
        TestItem.objects.using(self.using_destination).all().delete()
        OutgoingTransaction.objects.all().delete()
        OutgoingTransaction.objects.using(self.using_destination).all().delete()
        IncomingTransaction.objects.all().delete()
        IncomingTransaction.objects.using(self.using_source).all().delete()
        Producer.objects.using(self.using_source).delete()

        serialize_to_transaction = SerializeToTransaction(self.using_destination)
        self.assertEqual(serialize_to_transaction.get_using(), self.using_destination)
        serialize_to_transaction = SerializeToTransaction(using=self.using_source)
        self.assertEqual(serialize_to_transaction.get_using(), self.using_source)
        serialize_to_transaction = SerializeToTransaction()
        self.assertEqual(serialize_to_transaction.get_using(), 'default')

        deserialize_from_transaction = DeserializeFromTransaction(self.using_destination)
        self.assertEqual(deserialize_from_transaction.get_using(), self.using_destination)
        deserialize_from_transaction = DeserializeFromTransaction(using=self.using_source)
        self.assertEqual(deserialize_from_transaction.get_using(), self.using_source)
        deserialize_from_transaction = DeserializeFromTransaction()
        self.assertEqual(deserialize_from_transaction.get_using(), 'default')

        consumer = Consumer(using=self.using_destination)
        self.assertEqual(consumer.get_using(), self.using_destination)
        consumer = Consumer(using=self.using_source)
        self.assertEqual(consumer.get_using(), self.using_source)
        consumer = Consumer()
        self.assertEqual(consumer.get_using(), 'default')
