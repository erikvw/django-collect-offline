import datetime

from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.test import TestCase

from edc.core.bhp_content_type_map.models import ContentTypeMap
from edc.device.sync.classes import Consumer, DeserializeFromTransaction
from edc.device.sync.models import Producer, OutgoingTransaction, IncomingTransaction
from edc.subject.consent.models import ConsentCatalogue


class SyncMethodsTests(TestCase):

    def setUp(self):
        self.producer_name = 'lab_api'
        self.using_destination = 'lab_api'
        self.using_source = 'default'
        Producer.objects.using(self.using_source).delete()
        OutgoingTransaction.objects.using(self.using_destination).delete()
        IncomingTransaction.objects.using(self.using_source).delete()

    def test_fetch_outgoing(self):
        for i in range(1, 4):
            self.create_outgoing_transaction()
        self.create_producer(is_active=True)
        self.assertEqual(OutgoingTransaction.objects.using(self.using_destination).all().count(), 3)
        consumer = Consumer()
        consumer.fetch_outgoing(self.producer_name)
        self.assertEqual(OutgoingTransaction.objects.using(self.using_destination).filter(is_consumed=False).count(), 0)
        self.assertTrue(OutgoingTransaction.objects.using(self.using_destination).filter(is_consumed=True)[0].consumed_datetime.today())
        self.assertEqual(IncomingTransaction.objects.using(self.using_source).all().count(), 3)

    def test_consume(self):
        pass

    def test_copy_incoming_from_server(self):
        pass

    def test_transactions_sync_deserialize(self):
        self.assertEqual(OutgoingTransaction.objects.using(self.using_destination).all().count(), 0)
        self.assertEqual(OutgoingTransaction.objects.using(self.using_source).all().count(), 0)
        ContentType.objects.using(self.using_destination).create(name='consent',
                                                                    app_label='bh_consent',
                                                                    model='consent'
                                                                    )
        ContentTypeMap.objects.using(self.using_destination).create(content_type=ContentType.objects.using(self.using_destination).all()[0],
                                                                    name='consent',
                                                                    app_label='bh_consent',
                                                                    model='consent'
                                                                    )
        for i in range(1, 4):
            # save records into the remote database, these should create outgoing transactions
            ConsentCatalogue.objects.using(self.using_destination).create(name='year_1_consent',
                                                                    content_type_map=ContentTypeMap.objects.using(self.using_destination).all()[0],
                                                                    consent_type='initial',
                                                                    version=i,
                                                                    start_datetime=datetime.date.today(),
                                                                    end_datetime=datetime.date.today() + datetime.timedelta(days=10),
                                                                    list_for_update=True,
                                                                    add_for_app='mochudi',
                                                                    )
        # check the three exist in the remote database
        self.assertEqual(ConsentCatalogue.objects.using(self.using_destination).all().count(), 3)
        # self.print_queryset(OutgoingTransaction.objects.using(self.using_destination).all())
        # check that transactions where created.
        self.assertEqual(OutgoingTransaction.objects.using(self.using_destination).all().count(), 0)
        self.assertEqual(OutgoingTransaction.objects.using(self.using_source).all().count(), 3)
        # delete records in the producer
        ConsentCatalogue.objects.using(self.using_destination).all().delete()
        # check for one more outgoing transaction in the producer
        self.assertEqual(OutgoingTransaction.objects.using(self.using_destination).all().count(), 0)
        self.assertEqual(OutgoingTransaction.objects.using(self.using_source).all().count(), 6)

        self.create_producer()
        # sync outgoing transactions from the producer
        self.get_consumer_instance().fetch_from_producer(self.using_destination)
        # make sure all transactions were consumed from the producer
        self.assertFalse(OutgoingTransaction.objects.using(self.using_destination).filter(is_consumed=False).exists())
        # consume incoming transactions on the server
        call_command('consume', consume=True)
        # check all incoming transactions have been consumed
        self.assertFalse(IncomingTransaction.objects.using(self.using_destination).filter(is_consumed=False).exists())
        self.assertFalse(ConsentCatalogue.objects.using(self.using_destination).all().exists())

    def get_deserialize_from_transaction_instance(self):
        return DeserializeFromTransaction()

    def get_consumer_instance(self):
        return Consumer()

    def print_queryset(self, query_set):
        for i in query_set:
            print "*********" + str(i)

    def create_producer(self, is_active=False):
        # add a in_active producer
        Producer.objects.create(name=self.producer_name, settings_key=self.producer_name, is_active=is_active)
        # return Producer.objects.all()[0]

    def create_incoming_transaction(self):
        IncomingTransaction.objects.using(self.using_source).create(
            tx='tx',
            tx_pk='tx_pk',
            producer=self.using_source,
            is_consumed=False)

    def create_outgoing_transaction(self):
        OutgoingTransaction.objects.using(self.using_destination).create(
            tx='tx',
            tx_pk='tx_pk',
            producer=self.using_destination,
            is_consumed=False)
