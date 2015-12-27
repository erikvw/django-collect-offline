from datetime import date

from django.contrib.auth.models import User

from tastypie.models import ApiKey
from tastypie.test import ResourceTestCase
from edc_sync.tests.test_models import TestModel
from edc_sync.models.incoming_transaction import IncomingTransaction


class TestResource(ResourceTestCase):

    def setUp(self):
        super(TestResource, self).setUp()

        self.username = 'erik'
        self.password = 'pass'
        self.user = User.objects.create_user(self.username, 'erik@example.com', self.password)
        self.api_client_key = ApiKey.objects.get_or_create(user=self.user)[0].key

    def get_credentials(self):
        return self.create_apikey(username=self.username, api_key=self.api_client_key)

    def test_model(self):

        self.assertEqual(TestModel.objects.count(), 0)

        resource_data = {
            'target': 30,
            'is_consumed': False
        }
        self.assertHttpCreated(
            self.api_client.post(
                '/api/v1/outgoingtransaction/',
                format='json',
                data=resource_data,
                authentication=self.get_credentials()
            )
        )
        self.assertEqual(IncomingTransaction.objects.count(), 1)
