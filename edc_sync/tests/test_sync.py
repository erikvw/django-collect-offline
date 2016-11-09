from django.apps import apps as django_apps
from django.core.exceptions import MultipleObjectsReturned
from django.test.testcases import TestCase
from django.test.utils import override_settings

from edc_sync.exceptions import SyncModelError, SyncError
from edc_sync.models import OutgoingTransaction, IncomingTransaction

from edc_example.models import (
    TestModel, ComplexTestModel, Fk, M2m, TestEncryptedModel, BadTestModel, AnotherBadTestModel)

Crypt = django_apps.get_app_config('django_crypto_fields').model

edc_device_app_config = django_apps.get_app_config('edc_device')


class TestSync(TestCase):

    multi_db = True

    def get_credentials(self):
        return self.create_apikey(username=self.username, api_key=self.api_client_key)

    def test_raises_on_missing_natural_key(self):
        with override_settings(DEVICE_ID='10'):
            with self.assertRaises(SyncModelError) as cm:
                BadTestModel.objects.using('client').create()
            self.assertIn('natural_key', str(cm.exception))

    def test_raises_on_missing_get_by_natural_key(self):
        with override_settings(DEVICE_ID='10'):
            with self.assertRaises(SyncModelError) as cm:
                AnotherBadTestModel.objects.using('client').create()
            self.assertIn('get_by_natural_key', str(cm.exception))

    def test_creates_outgoing_on_add(self):
        with override_settings(DEVICE_ID='10'):
            test_model = TestModel.objects.using('client').create(f1='erik')
            with self.assertRaises(OutgoingTransaction.DoesNotExist):
                try:
                    OutgoingTransaction.objects.using('client').get(
                        tx_pk=test_model.pk, tx_name='edc_example.testmodel', action='I')
                except OutgoingTransaction.DoesNotExist:
                    pass
                else:
                    raise OutgoingTransaction.DoesNotExist()
            history_obj = test_model.history.using('client').get(id=test_model.id)
            with self.assertRaises(OutgoingTransaction.DoesNotExist):
                try:
                    OutgoingTransaction.objects.using('client').get(
                        tx_pk=history_obj.history_id, tx_name='edc_example.historicaltestmodel', action='I')
                except OutgoingTransaction.DoesNotExist:
                    pass
                else:
                    raise OutgoingTransaction.DoesNotExist()

    @override_settings(ALLOW_MODEL_SERIALIZATION=False)
    def test_does_not_create_outgoing(self):
        with override_settings(DEVICE_ID='10', ALLOW_MODEL_SERIALIZATION=False):
            test_model = TestModel.objects.using('client').create(f1='erik')
            with self.assertRaises(OutgoingTransaction.DoesNotExist):
                OutgoingTransaction.objects.using('client').get(tx_pk=test_model.pk)

    def test_creates_outgoing_on_change(self):
        with override_settings(DEVICE_ID='10'):
            test_model = TestModel.objects.using('client').create(f1='erik')
            test_model.save(using='client')
            with self.assertRaises(OutgoingTransaction.DoesNotExist):
                try:
                    OutgoingTransaction.objects.using('client').get(
                        tx_pk=test_model.pk, tx_name='edc_example.testmodel', action='I')
                    OutgoingTransaction.objects.using('client').get(
                        tx_pk=test_model.pk, tx_name='edc_example.testmodel', action='U')
                except OutgoingTransaction.DoesNotExist:
                    pass
                else:
                    raise OutgoingTransaction.DoesNotExist()
            self.assertEqual(
                2, OutgoingTransaction.objects.using('client').filter(
                    tx_name='edc_example.historicaltestmodel', action='I').count())

    def test_timestamp_is_default_order(self):
        with override_settings(DEVICE_ID='10'):
            test_model = TestModel.objects.using('client').create(f1='erik')
            test_model.save(using='client')
            last = 0
            for obj in OutgoingTransaction.objects.using('client').all():
                self.assertGreater(int(obj.timestamp), last)
                last = int(obj.timestamp)

    def test_created_obj_serializes_to_correct_db(self):
        """Asserts that the obj and the audit obj serialize to the correct DB in a multi-database environment."""
        TestModel.objects.using('client').create(f1='erik')
        result = [obj.tx_name for obj in OutgoingTransaction.objects.using('client').all()]
        result.sort()
        self.assertListEqual(
            result,
            [u'edc_example.historicaltestmodel', u'edc_example.testmodel'])
        self.assertListEqual([obj.tx_name for obj in OutgoingTransaction.objects.using('server').all()], [])
        self.assertRaises(OutgoingTransaction.DoesNotExist,
                          OutgoingTransaction.objects.using('server').get, tx_name='edc_example.testmodel')
        self.assertRaises(
            MultipleObjectsReturned,
            OutgoingTransaction.objects.using('client').get, tx_name__contains='testmodel')

    def test_updated_obj_serializes_to_correct_db(self):
        """Asserts that the obj and the audit obj serialize to the correct DB in a multi-database environment."""
        test_model = TestModel.objects.using('client').create(f1='erik')
        result = [obj.tx_name for obj in OutgoingTransaction.objects.using('client').filter(action='I')]
        result.sort()
        self.assertListEqual(
            [obj.tx_name for obj in OutgoingTransaction.objects.using('client').filter(action='I')],
            [u'edc_example.historicaltestmodel', u'edc_example.testmodel'])
        self.assertListEqual(
            [obj.tx_name for obj in OutgoingTransaction.objects.using('client').filter(action='U')],
            [])
        test_model.save(using='client')
        self.assertListEqual(
            [obj.tx_name for obj in OutgoingTransaction.objects.using('client').filter(action='U')],
            [u'edc_example.testmodel'])
        result = [obj.tx_name for obj in OutgoingTransaction.objects.using('client').filter(action='I')]
        result.sort()
        self.assertListEqual(
            result,
            [u'edc_example.historicaltestmodel', u'edc_example.historicaltestmodel', u'edc_example.testmodel'])

    def test_m2m(self):
        for name in ['m2m_name' + str(x) for x in range(0, 10)]:
            M2m.objects.using('client').create(name=name)
