from collect_offline_app.models import TestModel
from django.contrib.auth.models import User
from django.test import TestCase, tag
from django_collect_offline.site_offline_models import (
    AlreadyRegistered,
    ModelNotRegistered,
)
from django_collect_offline.site_offline_models import site_offline_models


class TestSiteSyncModels(TestCase):
    def setUp(self):
        site_offline_models.registry = {}
        site_offline_models.loaded = False
        self.offline_models = [
            "collect_offline_app.testmodel",
            "collect_offline_app.badtestmodel",
            "collect_offline_app.anotherbadtestmodel",
            "collect_offline_app.yetanotherbadtestmodel",
            "collect_offline_app.testmodelwithfkprotected",
            "collect_offline_app.testmodelwithm2m",
            "collect_offline_app.testofflinemodelnohistorymanager",
            "collect_offline_app.testofflinemodelnouuid",
        ]
        site_offline_models.register(models=self.offline_models)

    def test_site_offline_models(self):
        self.assertTrue(str(site_offline_models))
        self.assertTrue(repr(site_offline_models))

    def test_site_offline_models2(self):
        self.assertIn("collect_offline_app", site_offline_models.site_models())

    def test_already_registered(self):
        self.assertRaises(
            AlreadyRegistered,
            site_offline_models.register,
            models=["collect_offline_app.testmodel"],
        )

    def test_get_as_sync_model_ok(self):
        self.assertTrue(site_offline_models.get_wrapped_instance(TestModel()))

    def test_get_as_sync_model_not_registered(self):
        user = User()
        self.assertRaises(
            ModelNotRegistered, site_offline_models.get_wrapped_instance, user
        )

    def test_get_as_sync_model_none(self):
        self.assertRaises(AttributeError, site_offline_models.get_wrapped_instance)
