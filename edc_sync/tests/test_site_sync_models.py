from django.contrib.auth.models import User
from django.test import TestCase, tag
from edc_base.site_models import SiteModelAlreadyRegistered, SiteModelNotRegistered

from ..site_sync_models import site_sync_models
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
        site_sync_models.register(models=self.sync_models)

    def test_site_sync_models(self):
        self.assertTrue(str(site_sync_models))
        self.assertTrue(repr(site_sync_models))

    def test_site_sync_models2(self):
        self.assertIn('edc_sync', site_sync_models.site_models())

    def test_already_registered(self):
        self.assertRaises(
            SiteModelAlreadyRegistered,
            site_sync_models.register,
            models=['edc_sync.testmodel'])

    def test_get_as_sync_model_ok(self):
        self.assertTrue(
            site_sync_models.get_wrapped_instance(TestModel()))

    def test_get_as_sync_model_not_registered(self):
        user = User()
        self.assertRaises(
            SiteModelNotRegistered,
            site_sync_models.get_wrapped_instance, user)

    def test_get_as_sync_model_none(self):
        self.assertRaises(
            AttributeError,
            site_sync_models.get_wrapped_instance)
