from django.db import models
from django.test.utils import override_settings

from edc_base.model.models import BaseUuidModel
from edc_device.device import DeviceClass
from edc_sync.exceptions import SyncError
from edc_sync.models import SyncModelMixin, OutgoingTransaction
from edc_sync.models.incoming_transaction import IncomingTransaction

from .test_models import TestModel, ComplexTestModel, Fk, M2m
from django.test.testcases import TransactionTestCase
from django.core.exceptions import MultipleObjectsReturned


class BadTestModel(SyncModelMixin, BaseUuidModel):
    """A test model that is missing natural_key and get_by_natural_key."""

    f1 = models.CharField(max_length=10, default='f1')

    objects = models.Manager()

    class Meta:
        app_label = 'edc_sync'


class AnotherBadTestModel(SyncModelMixin, BaseUuidModel):
    """A test model that is missing get_by_natural_key."""

    f1 = models.CharField(max_length=10, default='f1')

    objects = models.Manager()

    def natural_key(self):
        return (self.f1, )

    class Meta:
        app_label = 'edc_sync'


class TestSync(TransactionTestCase):

    def setUp(self):
        TestModel.objects.using('other').delete()
        TestModel.history.model.objects.using('other').delete()
        OutgoingTransaction.objects.using('other').delete()
        self.assertEqual(IncomingTransaction.objects.using('other').all().count(), 0)
        self.assertEqual(IncomingTransaction.objects.using('default').all().count(), 0)
        self.assertEqual(OutgoingTransaction.objects.using('other').all().count(), 0)
        self.assertEqual(OutgoingTransaction.objects.using('default').all().count(), 0)

    def get_credentials(self):
        return self.create_apikey(username=self.username, api_key=self.api_client_key)

    def test_raises_on_missing_natural_key(self):
        with self.assertRaises(SyncError) as cm:
            BadTestModel.objects.create()
        self.assertIn('natural_key', str(cm.exception))

    def test_raises_on_missing_get_by_natural_key(self):
        with self.assertRaises(SyncError) as cm:
            AnotherBadTestModel.objects.create()
        self.assertIn('get_by_natural_key', str(cm.exception))

    def test_creates_outgoing_on_add(self):
        test_model = TestModel.objects.create(f1='erik')
        with self.assertRaises(OutgoingTransaction.DoesNotExist):
            try:
                OutgoingTransaction.objects.get(tx_pk=test_model.pk, tx_name='TestModel', action='I')
            except OutgoingTransaction.DoesNotExist:
                pass
            else:
                raise OutgoingTransaction.DoesNotExist()
        with self.assertRaises(OutgoingTransaction.DoesNotExist):
            try:
                OutgoingTransaction.objects.get(tx_pk=test_model.pk, tx_name='TestModelAudit', action='I')
            except OutgoingTransaction.DoesNotExist:
                pass
            else:
                raise OutgoingTransaction.DoesNotExist()

    @override_settings(ALLOW_MODEL_SERIALIZATION=False)
    def test_does_not_create_outgoing(self):
        test_model = TestModel.objects.create(f1='erik')
        with self.assertRaises(OutgoingTransaction.DoesNotExist):
            OutgoingTransaction.objects.get(tx_pk=test_model.pk)

    def test_creates_outgoing_on_change(self):
        test_model = TestModel.objects.create(f1='erik')
        test_model.save()
        with self.assertRaises(OutgoingTransaction.DoesNotExist):
            try:
                OutgoingTransaction.objects.get(tx_pk=test_model.pk, tx_name='TestModel', action='I')
                OutgoingTransaction.objects.get(tx_pk=test_model.pk, tx_name='TestModel', action='U')
            except OutgoingTransaction.DoesNotExist:
                pass
            else:
                raise OutgoingTransaction.DoesNotExist()
        self.assertEqual(
            2, OutgoingTransaction.objects.filter(tx_pk=test_model.pk, tx_name='TestModelAudit', action='I').count())

    def test_timestamp_is_default_order(self):
        test_model = TestModel.objects.create(f1='erik')
        test_model.save()
        last = 0
        for obj in OutgoingTransaction.objects.all():
            self.assertGreater(int(obj.timestamp), last)
            last = int(obj.timestamp)

    def test_deserialize_fails_not_server(self):
        device = DeviceClass(device_id='10')
        self.assertFalse(device.is_server)
        TestModel.objects.create(f1='erik')
        self.assertRaises(SyncError, IncomingTransaction.objects.deserialize, custom_device=device)

    def test_deserialize_succeeds_as_server(self):
        device = DeviceClass(device_id='99')
        self.assertTrue(device.is_server)
        TestModel.objects.create(f1='erik')
        with self.assertRaises(SyncError):
            try:
                IncomingTransaction.objects.deserialize(custom_device=device)
            except:
                pass
            else:
                raise SyncError()

#     def test_resource(self):
#         TestModel.objects.using('other').create(f1='erik')

    def test_copy_db_to_db(self):
        TestModel.objects.using('other').create(f1='erik')
        self.assertEqual(
            IncomingTransaction.objects.using('default').all().count(), 0)
        for obj in OutgoingTransaction.objects.using('other').all():
            obj.copy_to_incoming_transaction('default')
        self.assertEquals(
            OutgoingTransaction.objects.using('other').all().count(),
            IncomingTransaction.objects.using('default').all().count())

    def test_deserialize_insert(self):
        device = DeviceClass(device_id='99')
        TestModel.objects.using('other').create(f1='erik')
        for obj in OutgoingTransaction.objects.using('other').all():
            obj.copy_to_incoming_transaction('default')
        messages = IncomingTransaction.objects.deserialize(custom_device=device, check_hostname=False)
        self.assertEqual(2, len(messages))
        for message in messages:
            self.assertEqual((1, 0, 0), (message.inserted, message.updated, message.deleted))
        with self.assertRaises(TestModel.DoesNotExist):
            try:
                TestModel.objects.get(f1='erik')
            except:
                pass
            else:
                raise TestModel.DoesNotExist

    def test_deserialize_update(self):
        device = DeviceClass(device_id='99')
        test_model = TestModel.objects.using('other').create(f1='erik')
        for obj in OutgoingTransaction.objects.using('other').all():
            obj.copy_to_incoming_transaction('default')
        IncomingTransaction.objects.deserialize(custom_device=device, check_hostname=False)
        self.assertEqual(0, IncomingTransaction.objects.filter(is_consumed=False).count())
        test_model.save()
        for obj in OutgoingTransaction.objects.using('other').all():
            obj.copy_to_incoming_transaction('default')
        messages = IncomingTransaction.objects.deserialize(custom_device=device, check_hostname=False)
        self.assertEqual(2, len(messages))
        for message in messages:
            if message.tx_name == 'TestModel':
                self.assertEqual((0, 1, 0), (message.inserted, message.updated, message.deleted))
            if message.tx_name == 'TestModelAudit':
                self.assertEqual((1, 0, 0), (message.inserted, message.updated, message.deleted))

        with self.assertRaises(TestModel.DoesNotExist):
            try:
                TestModel.objects.get(f1='erik')
            except:
                pass
            else:
                raise TestModel.DoesNotExist

    def test_created_obj_serializes_to_correct_db(self):
        """Asserts that the obj and the audit obj serialize to the correct DB in a multi-database environment."""
        TestModel.objects.using('other').create(f1='erik')
        self.assertListEqual(
            [obj.tx_name for obj in OutgoingTransaction.objects.using('other').all()],
            [u'TestModel', u'TestModelAudit'])
        self.assertListEqual([obj.tx_name for obj in OutgoingTransaction.objects.using('default').all()], [])
        self.assertRaises(OutgoingTransaction.DoesNotExist,
                          OutgoingTransaction.objects.using('default').get, tx_name='TestModel')
        self.assertRaises(
            MultipleObjectsReturned,
            OutgoingTransaction.objects.using('other').get, tx_name__contains='TestModel')

    def test_updated_obj_serializes_to_correct_db(self):
        """Asserts that the obj and the audit obj serialize to the correct DB in a multi-database environment."""
        test_model = TestModel.objects.using('other').create(f1='erik')
        self.assertListEqual(
            [obj.tx_name for obj in OutgoingTransaction.objects.using('other').filter(action='I')],
            [u'TestModel', u'TestModelAudit'])
        self.assertListEqual(
            [obj.tx_name for obj in OutgoingTransaction.objects.using('other').filter(action='U')],
            [])
        test_model.save()
        self.assertListEqual(
            [obj.tx_name for obj in OutgoingTransaction.objects.using('other').filter(action='U')],
            [u'TestModel'])
        self.assertListEqual(
            [obj.tx_name for obj in OutgoingTransaction.objects.using('other').filter(action='I')],
            [u'TestModel', u'TestModelAudit', u'TestModelAudit'])

    def test_complex_model(self):
        device = DeviceClass(device_id='99')
        for name in 'abcdefg':
            fk = Fk.objects.using('other').create(name=name)
        ComplexTestModel.objects.using('other').create(f1='1', fk=fk)
        for obj in OutgoingTransaction.objects.using('other').all():
            obj.copy_to_incoming_transaction('default')
        print(IncomingTransaction.objects.all().count())
        messages = IncomingTransaction.objects.deserialize(custom_device=device, check_hostname=False)
        for message in messages:
            print(message)
