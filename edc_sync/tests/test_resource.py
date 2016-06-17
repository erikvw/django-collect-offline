from django.contrib.auth.models import User

from tastypie.models import ApiKey
from tastypie.test import ResourceTestCaseMixin

from edc_sync.models import OutgoingTransaction

from example.models import TestModel
from django.test.testcases import TestCase


class TestResource(ResourceTestCaseMixin, TestCase):

    def setUp(self):
        super(TestResource, self).setUp()
        self.username = 'erik'
        self.password = 'pass'
        self.user = User.objects.create_user(
            self.username, 'erik@example.com', self.password)
        self.user.save()
        self.api_client_key = ApiKey.objects.get_or_create(user=self.user)[0].key

    def get_credentials(self):
        return self.create_apikey(username=self.username, api_key=self.api_client_key)

    def test_get_list_unauthorzied(self):
        self.assertHttpUnauthorized(self.api_client.get('/api/v1/outgoingtransaction/', format='json'))

    def test_get_valid_json(self):
        TestModel.objects.create(f1='f1')
        self.assertEqual(TestModel.objects.count(), 1)
        self.assertEqual(OutgoingTransaction.objects.filter(tx_name='TestModel').count(), 1)
        pk = OutgoingTransaction.objects.filter(tx_name='TestModel')[0].pk
        resp = self.api_client.get(
            '/api/v1/outgoingtransaction/' + str(pk) + '/',
            format='json',
            authentication=self.get_credentials()
        )
        self.assertValidJSONResponse(resp)
        self.assertKeys(self.deserialize(resp), ['meta', 'objects'])

    def test_get_paginates(self):
        for n in range(0, 20):
            TestModel.objects.create(f1='f{}'.format(n))
        self.assertEqual(TestModel.objects.count(), 20)
        self.assertEqual(OutgoingTransaction.objects.filter(
            tx_name__icontains='TestModel', is_consumed_server=False).count(), 40)
        resource_data = {'target': 2}
        resp = self.api_client.get(
            '/api/v1/outgoingtransaction/',
            format='json',
            # data={},
            authentication=self.get_credentials()
        )
        self.assertValidJSONResponse(resp)
        print(resp.__dict__)
        self.assertEqual(len(self.deserialize(resp)['objects']), 20)

    def test_get_is_consumed_middleman(self):
        for n in range(0, 20):
            TestModel.objects.create(f1='f{}'.format(n))
        for n in range(0, 5):
            obj = OutgoingTransaction.objects.filter(tx_name='TestModel').order_by('timestamp')[n]
            obj.is_consumed_middleman = True
            obj.save()
        for n in range(0, 5):
            obj = OutgoingTransaction.objects.filter(tx_name='TestModelAudit').order_by('timestamp')[n]
            obj.is_consumed_middleman = True
            obj.save()
        resource_data = {
            'is_consumed_middleman': True}
        resp = self.api_client.get(
            '/api/v1/outgoingtransaction/',
            format='json',
            data=resource_data,
            authentication=self.get_credentials()
        )
        self.assertEqual(len(self.deserialize(resp)['objects']), 10)

    def test_get_is_consumed_server_always_false(self):
        for n in range(0, 10):
            TestModel.objects.create(f1='f{}'.format(n))
        for n in range(0, 5):
            obj = OutgoingTransaction.objects.filter(tx_name='TestModel').order_by('timestamp')[n]
            obj.is_consumed_server = True
            obj.save()
        for n in range(0, 5):
            obj = OutgoingTransaction.objects.filter(tx_name='TestModelAudit').order_by('timestamp')[n]
            obj.is_consumed_server = True
            obj.save()
        resp = self.api_client.get(
            '/api/v1/outgoingtransaction/',
            format='json',
            data={},
            authentication=self.get_credentials()
        )
        self.assertEqual(len(self.deserialize(resp)['objects']), 10)
