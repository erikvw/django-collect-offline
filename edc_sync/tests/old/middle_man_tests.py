from django.contrib.auth.models import User

from ..models import OutgoingTransaction

from .base_sync_device_tests import BaseSyncDeviceTests
from .factories import MiddleManTransactionFactory, ProducerFactory


class MiddleManTests(BaseSyncDeviceTests):

    def test_middleman_settings(self):
        self.device.set_device_id(99)
        self.assertRaises(TypeError, lambda: MiddleManTransactionFactory())

    def test_tastypie_synchronizing_link(self):
        producer = 'bcpp039-bhp066'
        app_name = 'bcpp'
        ProducerFactory(name=producer, settings_key=producer, url='http://localhost:8000/')
        self.device.set_device_id(98)
        self.assertEqual(User.objects.all().count(), 1)
        self.assertEqual(ApiKey.objects.all().count(), 1)
        self.denies_anonymous_acess(producer, app_name)
        print('Number of OUTGOING TRANSACTIONS = {0}'.format(OutgoingTransaction.objects.all().count()))
        # FIXME: use reverse
        response = self.client.get('/bhp_sync/consume/' + producer + '/' + app_name + '/', follow=True)
        # FIXME: use reverse
        self.assertTrue(str(response).find('/bhp_sync/api_otmr/outgoingtransaction') != -1)
        self.assertEqual(response.status_code, 200)
        # FIXME: use reverse
        self.assertRedirects(response, '/dispatch/bcpp/sync/' + producer + '/')
