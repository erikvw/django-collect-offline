from django.contrib.auth.management.commands import changepassword
from django.contrib.auth.models import User
from django.core import management
from django.test import TestCase

from tastypie.models import ApiKey

from edc_device import device

from ..models import OutgoingTransaction, IncomingTransaction, MiddleManTransaction


class BaseSyncDeviceTests(TestCase):

    def setUp(self):
        OutgoingTransaction.objects.all().delete()
        IncomingTransaction.objects.all().delete()
        MiddleManTransaction.objects.all().delete()
        management.call_command('createsuperuser', interactive=False, username="john", email="xxx@xxx.it")
        command = changepassword.Command()
        command._get_pass = lambda *args: 'smith'
        command.execute("john")
        if not ApiKey.objects.filter(user=User.objects.get(username='john')):
            ApiKey.objects.create(user=User.objects.get(username='john'))
        self.device = device

    def denies_anonymous_acess(self, producer, app_name):
        response = self.client.get('/bhp_sync/consume/' + producer + '/' + app_name + '/', follow=True)
        self.assertRedirects(response, '/bcpp/login/?next=/bhp_sync/consume/' + producer + '/' + app_name + '/')
        self.client.post('/bcpp/login/', {'username': 'john', 'password': 'smith'})
