from django.test.testcases import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from rest_framework.test import APIRequestFactory
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from edc_sync.models import History


class TestFetchMediaFiles(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        user = User.objects.create(
            username='django',
            password='password'
        )
        Token.objects.create(
            user=user
        )

    def test_get_pending_media_files(self):
        token = Token.objects.get(user__username='django')
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        request = client.get(reverse("pending-media-count"))
        print(request.data)

    def test_put_history(self):
        self.factory.put(reverse("edc-sync:create-history"), {'filename': 'New File Name'})
        self.assertEqual(1, History.objects.all().count())

    def test_client_put_history(self):
        token = Token.objects.get(user__username='django')
        client = APIClient(enforce_csrf_checks=True)
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        client.put(reverse("edc-sync:create-history"), {'filename': 'New File Name'}, format='json')
        self.assertEqual(1, History.objects.all().count())
