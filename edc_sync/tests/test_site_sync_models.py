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
