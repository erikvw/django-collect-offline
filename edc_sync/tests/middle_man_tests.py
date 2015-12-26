from django.contrib.auth.models import User

from tastypie.models import ApiKey

from ..models import OutgoingTransaction

from .base_sync_device_tests import BaseSyncDeviceTests
from .factories import MiddleManTransactionFactory, ProducerFactory


class MiddleManTests(BaseSyncDeviceTests):

    def test_middleman_settings(self):
        # if not device.is_middleman:
        self.device.set_device_id(99)
        self.assertRaises(TypeError, lambda: MiddleManTransactionFactory())

    def test_requisition_inspector(self):
        raise
# doesn't belong in edc module
#         from .apps.bcpp_inspector.models import SubjectRequisitionInspector
#         # if device.is_middleman:
#         settings.DEVICE_ID = '98'
#         wb_requisition = MiddleManTransactionFactory()#default middle man transaction is wb requisition.
#
#         encrypted_transaction = 'enc1:::c4edcf6497a97d1dc2e98738710e7c2fae0768871016792b368dddd76c189481enc2:::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:::XRzo4QRQ/OAQu1rL6KfP+g=='
#         tx_pk = '6936236f-b468-4cdc-8bff-9334b75339f9'
#         timestamp = '20130815142355618511'
#         tx_name = 'SubjectRequisition'
#         second_requisition = MiddleManTransactionFactory(tx=encrypted_transaction, tx_pk=tx_pk, timestamp=timestamp, tx_name=tx_name)
#
#         self.assertEqual(SubjectRequisitionInspector.objects.all().count(),2)
#         print 'Number of Req Inspectors so far: {0}'.format(SubjectRequisitionInspector.objects.all().count())
#         encrypted_transaction2 = 'enc1:::c3e0fe36af2f7f0d14ed8734a3e26922857ce297d2e2e845e9da09b8455904aaenc2:::5X9MpVIyvHdgCNv0DqUo8HrkMTSvYccsPu2hXOgYuMdUnyGBI22MLO8K+0b5mZ1Xz5vp2Tfno8TVJK/o84gWEglll77eTWD6Xx1termZA7Hy60xb63ZfkOpGjXXGHzCGS5V/En0SZMdYIpYIBEsT9kt0sBxCQGBm3LG2/jnp56H/YDXkOkOLlHYotzsl2ta0DMKuzakcpC8qJXG6OTnvHdV4dUKGnIPeT9Tnd7jsUzmMPkWVmw3kqK2J3kAnibt3DdDUp5Ki7HIC8FHBvnZ8+OUnt+m8PvRZZl+eOlkvsvjqHOadAQPl0nA1pqdDjZj9WU7OGAyGphuqPBGstdM72aNLZKxTPWgrv4wdyITolaEr/5lmQr5Qo6uEtENTkrA1ZL0T2hlB0AAV++M53weeJuxEiy3vW/Mj0/obU+K/gMk9IVdvYo/kRyW9uv80hI9NyODUqb5OlqG/Dl5nthbsiPfKdHRQAmG8kkcGhTyS6G4ZtCLHgPQ86zfdrYjBUColN6T8PEBJCQY5M1w5WJlgkbFH733jB7WLAME35zQY61e3Zibvf6cBRVkCgZu7xYXT2nf69Vq0qfs3T3gSq0A1zNbymRy0qwd8Mm5iHbT206xjxSP8R/79MP0+zjPj86nNuyWaJiM7qI/UPQDsW6xYDQk25ENSL8K4RSsN4s0beaxL1MuqOc1T9+5taA5VwKOx9ieVTRqm44u45KHKS/MagvnTMBJToNLb9VcMqjL/ZfynGrlTueKFhP+8KvMN1FTobb9M7oClmMDd/sO7qUR9FDIQSmNzsI50M7hw2+Bdf0drX7WvukvcCZvchX1zHL3dl0Nwe3Gkt3kVkRG/QyYdbJyhmYiFPIP5ertC1rAvy9f5If2W5O6P92Ie2uxTUZhuNsE+apWskX9DNyld/mHCtdTV2Y9zibUR/KkBz0kQXq41HeFAOe1/qWzvhnXF77Lv3q79uyZeGT1wxiB3BYpBg/dhDnUs06Ij2sK0+CXvP+AXjKbRfWBVWiGxwT8b4hzuIyt/eHP8phskEsDV9jgLKucADOF68vZegUTwjOcR6Go=iv:::rFDEkMr0iMoO10lvpleimw=='
#         tx_pk2 = '52767db0-fe38-4c83-b329-a5bc68410696'
#         timestamp2 = '20130809152815489937'
#         tx_name = 'HouseholdStructure'
#         household_structure = MiddleManTransactionFactory(tx=encrypted_transaction2, tx_pk=tx_pk2, timestamp=timestamp2, tx_name=tx_name)
#         self.assertEqual(SubjectRequisitionInspector.objects.all().count(),2)
#         self.assertEqual(MiddleManTransaction.objects.all().count(),3)
#         print 'Number of Middle Men Transactions so far: {0}'.format(MiddleManTransaction.objects.all().count())

    def test_tastypie_synchronizing_link(self):
        producer = 'bcpp039-bhp066'
        app_name = 'bcpp'
        ProducerFactory(name=producer, settings_key=producer, url='http://localhost:8000/')
        self.device.set_device_id(98)
        self.assertEqual(User.objects.all().count(), 1)
        self.assertEqual(ApiKey.objects.all().count(), 1)
        self.denies_anonymous_acess(producer, app_name)
        print 'Number of OUTGOING TRANSACTIONS = {0}'.format(OutgoingTransaction.objects.all().count())
        # FIXME: use reverse
        response = self.client.get('/bhp_sync/consume/' + producer + '/' + app_name + '/', follow=True)
        # FIXME: use reverse
        self.assertTrue(str(response).find('/bhp_sync/api_otmr/outgoingtransaction') != -1)
        self.assertEqual(response.status_code, 200)
        # FIXME: use reverse
        self.assertRedirects(response, '/dispatch/bcpp/sync/' + producer + '/')
