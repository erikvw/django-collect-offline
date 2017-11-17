from django.contrib.auth.models import User
from django.test import TestCase

from ..site_sync_models import site_sync_models, M, SiteSyncModelError
from ..site_sync_models import SiteSyncModelNotRegistered, SiteSyncModelAlreadyRegistered
from ..sync_model import SyncModel
from .models import TestModel


class TestSiteSyncModels(TestCase):

    def setUp(self):
        site_sync_models.registry = {}
        site_sync_models.loaded = False
        self.sync_models = ['edc_sync.testmodel',
                            'edc_sync.badtestmodel',
                            'edc_sync.anotherbadtestmodel',
                            'edc_sync.yetanotherbadtestmodel',
                            'edc_sync.testmodelwithfkprotected',
                            'edc_sync.testmodelwithm2m',
                            'edc_sync.testsyncmodelnohistorymanager',
                            'edc_sync.testsyncmodelnouuid']
        site_sync_models.register(self.sync_models, SyncModel)

    def test_site_sync_models(self):
        self.assertTrue(str(site_sync_models))
        self.assertTrue(repr(site_sync_models))

    def test_site_sync_models2(self):
        self.assertIn('edc_sync', site_sync_models.site_models())

    def test_site_sync_models3(self):
        self.assertIn('auth', site_sync_models.site_models(sync=False))

    def test_site_sync_models4(self):
        self.assertIn('edc_sync', site_sync_models.site_models(sync=True))

    def test_site_sync_models_M(self):
        self.assertFalse(M(model='edc_sync.outgoingtransaction').sync)
        self.assertTrue(M(model='edc_sync.testmodel').sync)

    def test_site_sync_models_M2(self):
        self.assertTrue(str(M(model='edc_sync.outgoingtransaction')))
        self.assertTrue(repr(M(model='edc_sync.outgoingtransaction')))

    def test_already_registered(self):
        self.assertRaises(
            SiteSyncModelAlreadyRegistered,
            site_sync_models.register, ['edc_sync.testmodel'], SyncModel)

    def test_get_as_sync_model_ok(self):
        self.assertTrue(
            site_sync_models.get_as_sync_model(TestModel()))

    def test_get_as_sync_model_not_registered(self):
        user = User()
        self.assertRaises(
            SiteSyncModelNotRegistered,
            site_sync_models.get_as_sync_model, user)

    def test_get_as_sync_model_none(self):
        self.assertRaises(
            SiteSyncModelError,
            site_sync_models.get_as_sync_model)


# data = {'csrfmiddlewaretoken': ['Xm6F4tugr7JdBmasncfdBmHyF2Q32fV1ycFykZN5ubPdRDX3MWFCQZoGTPBsFC2u'],
# 'f1': ['field 1'],
# 'f2': ['field 2'],
# 'f3': ['ebb5538e'],
# 'testmodelwithfkprotected1_set-TOTAL_FORMS': ['6'],
# 'testmodelwithfkprotected1_set-INITIAL_FORMS': ['3'],
# 'testmodelwithfkprotected1_set-MIN_NUM_FORMS': ['0'],
# 'testmodelwithfkprotected1_set-MAX_NUM_FORMS': ['1000'],
#
# 'testmodelwithfkprotected1_set-0-id': ['3bde52f9-be5f-4d5f-b911-061aef90b8a4'],
# 'testmodelwithfkprotected1_set-0-test_model': ['c0a6d244-f1ed-405c-b2b2-187b194b0eea'],
# 'testmodelwithfkprotected1_set-0-device_created': ['15'],
# 'testmodelwithfkprotected1_set-0-device_modified': ['15'],
# 'testmodelwithfkprotected1_set-0-f1': ['inline 3'],
#
# 'testmodelwithfkprotected1_set-1-id': ['dad7beb3-786c-4390-9442-4fe09f6e7376'],
# 'testmodelwithfkprotected1_set-1-test_model': ['c0a6d244-f1ed-405c-b2b2-187b194b0eea'],
# 'testmodelwithfkprotected1_set-1-device_created': ['15'],
# 'testmodelwithfkprotected1_set-1-device_modified': ['15'],
# 'testmodelwithfkprotected1_set-1-f1': ['inline 2'],
#
# 'testmodelwithfkprotected1_set-2-id': ['b265b8b4-ec9f-42e2-9b57-6f622389533a'],
# 'testmodelwithfkprotected1_set-2-test_model': ['c0a6d244-f1ed-405c-b2b2-187b194b0eea'],
# 'testmodelwithfkprotected1_set-2-device_created': ['15'],
# 'testmodelwithfkprotected1_set-2-device_modified': ['15'], 'testmodelwithfkprotected1_set-2-f1': ['inline 1'],
# 'testmodelwithfkprotected1_set-3-id': [''],
# 'testmodelwithfkprotected1_set-3-test_model': ['c0a6d244-f1ed-405c-b2b2-187b194b0eea'],
# 'testmodelwithfkprotected1_set-3-device_created': [''],
# 'testmodelwithfkprotected1_set-3-device_modified': [''],
# 'testmodelwithfkprotected1_set-3-f1': [''],
# 'testmodelwithfkprotected1_set-4-id': [''],
# 'testmodelwithfkprotected1_set-4-test_model': ['c0a6d244-f1ed-405c-b2b2-187b194b0eea'], 'testmodelwithfkprotected1_set-4-device_created': [''], 'testmodelwithfkprotected1_set-4-device_modified': [''], 'testmodelwithfkprotected1_set-4-f1': [''], 'testmodelwithfkprotected1_set-5-id': [''], 'testmodelwithfkprotected1_set-5-test_model': ['c0a6d244-f1ed-405c-b2b2-187b194b0eea'], 'testmodelwithfkprotected1_set-5-device_created': [''], 'testmodelwithfkprotected1_set-5-device_modified': [''], 'testmodelwithfkprotected1_set-5-f1': [''], 'testmodelwithfkprotected1_set-__prefix__-id': [''], 'testmodelwithfkprotected1_set-__prefix__-test_model': ['c0a6d244-f1ed-405c-b2b2-187b194b0eea'], 'testmodelwithfkprotected1_set-__prefix__-device_created': [''], 'testmodelwithfkprotected1_set-__prefix__-device_modified': [''], 'testmodelwithfkprotected1_set-__prefix__-f1': [''], '_save': ['Save']}>
