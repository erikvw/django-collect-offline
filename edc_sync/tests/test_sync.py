from django.db import models
from django.test import TestCase
from django.test.utils import override_settings

from edc_base.model.models import BaseUuidModel
from edc_sync.exceptions import SyncError
from edc_sync.models import SyncModelMixin, OutgoingTransaction
from edc_sync.models.incoming_transaction import IncomingTransaction

from .test_models import TestModel


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


class TestSync(TestCase):

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

    @override_settings(DEVICE_ID='10')
    def test_deserialize_fails_not_server(self):
        TestModel.objects.create(f1='erik')
        self.assertRaises(SyncError, IncomingTransaction.objects.deserialize)

    def test_deserialize_server(self):
        TestModel.objects.create(f1='erik')
        with self.assertRaises(SyncError) as cm:
            try:
                IncomingTransaction.objects.deserialize(ignore_device_id=True)
            except cm.expected:
                pass
            else:
                raise SyncError()

    def test_resource(self):
        TestModel.objects.using('other').create(f1='erik')

    def test_deserialize_server2(self):
        TestModel.objects.using('other').create(f1='erik')
        self.assertRaises(TestModel.DoesNotExist, TestModel.objects.get, f1='erik')
        
        saved, new = IncomingTransaction.objects.deserialize(ignore_device_id=True)
        self.assertEqual((0, 0), (saved, new))
        self.assertRaises(TestModel.DoesNotExist, TestModel.objects.get, f1='erik')
        # self.assertRaises(SyncError, IncomingTransaction.objects.deserialize)
