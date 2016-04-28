import socket

from django.contrib.auth.models import User

from tastypie.models import ApiKey
from tastypie.test import ResourceTestCase

from edc_sync.views import ConsumeTransactions
from django.test.client import RequestFactory
from edc_sync.models.producer import Producer
from django.test.utils import override_settings
from edc_sync.exceptions import SyncError


class TestConsumeRest(ResourceTestCase):
    """Not ready...."""
    def setUp(self):
        super(TestConsumeRest, self).setUp()

        self.username = 'erik'
        self.password = 'pass'
        self.user = User.objects.create_user(
            self.username, 'erik@example.com', self.password)
        self.user.save()
        self.api_client_key = ApiKey.objects.get_or_create(user=self.user)[0].key
        hostname = socket.gethostname()
        using = 'client'
        self.producer_name = '{}-{}'.format(hostname, using)
        self.producer = Producer.objects.get_or_create(name=self.producer_name)
        self.request = RequestFactory()
        self.request.user = self.user

    def get_credentials(self):
        return self.create_apikey(username=self.username, api_key=self.api_client_key)

    @override_settings(DEVICE_ID='12')
    def test_must_be_server(self):
        self.assertRaises(SyncError, ConsumeTransactions, self.request, self.producer_name)

    @override_settings(DEVICE_ID='99')
    def test_rest_init(self):
        ConsumeTransactions(
            self.request, self.producer_name)

    @override_settings(DEVICE_ID='99')
    def test_rest_consume(self):
        consume_transactions = ConsumeTransactions(
            self.request, self.producer_name)
        consume_transactions.consume()
