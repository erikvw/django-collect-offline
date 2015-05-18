import socket

from tastypie.models import ApiKey

from django.conf import settings
from django.contrib.auth.models import User

from ..models import OutgoingTransaction

from .base_sync_device_tests import BaseSyncDeviceTests
from .factories import ProducerFactory


class ServerTests(BaseSyncDeviceTests):

    def test_server_settings(self):
        self.assertTrue(self.device.device_id == '99')

    def test_tastypie_synchronizing_link(self):
        producer = 'bcpp039-bhp066'
        app_name = 'bcpp'
        ProducerFactory(name=producer, settings_key=producer, url='http://localhost:8000/')
        self.device.set_device_id(99)
        self.assertEqual(User.objects.all().count(), 1)
        self.assertEqual(ApiKey.objects.all().count(), 1)
        self.denies_anonymous_acess(producer, app_name)
        print 'Number of OUTGOING TRANSACTIONS = {0}'.format(OutgoingTransaction.objects.all().count())
        #print response
        if not socket.gethostname() + '-bhp066' in settings.MIDDLE_MAN_LIST:
            response = self.client.get('/bhp_sync/consume/' + producer + '/' + app_name + '/', follow=True)
            self.assertTrue(str(response).find('/bhp_sync/api_otsr/outgoingtransaction') != -1)
            self.assertFalse(str(response).find('/bhp_sync/api_mmtr/middlemantransaction') != -1)
        elif socket.gethostname() + '-bhp066' in settings.MIDDLE_MAN_LIST:
            settings.MIDDLE_MAN_LIST.append(socket.gethostname() + '-bhp066')
            response = self.client.get('/bhp_sync/consume/' + producer + '/' + app_name + '/', follow=True)
            self.assertTrue(str(response).find('/bhp_sync/api_mmtr/middlemantransaction') != -1)
            self.assertFalse(str(response).find('/bhp_sync/api_otsr/outgoingtransaction') != -1)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/dispatch/bcpp/sync/' + producer + '/')

    def test_consume_from_usb(self):
        pass
