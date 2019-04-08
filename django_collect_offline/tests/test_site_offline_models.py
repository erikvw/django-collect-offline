from django.contrib.auth.models import User
from django.test import TestCase, tag

from ..site_offline_models import site_offline_models
from ..site_offline_models import AlreadyRegistered, ModelNotRegistered
from .models import TestModel


class TestSiteSyncModels(TestCase):
    def setUp(self):
        site_offline_models.registry = {}
        site_offline_models.loaded = False
        self.offline_models = [
            "django_collect_offline.testmodel",
            "django_collect_offline.badtestmodel",
            "django_collect_offline.anotherbadtestmodel",
            "django_collect_offline.yetanotherbadtestmodel",
            "django_collect_offline.testmodelwithfkprotected",
            "django_collect_offline.testmodelwithm2m",
            "django_collect_offline.testofflinemodelnohistorymanager",
            "django_collect_offline.testofflinemodelnouuid",
        ]
        site_offline_models.register(models=self.offline_models)

    def test_site_offline_models(self):
        self.assertTrue(str(site_offline_models))
        self.assertTrue(repr(site_offline_models))

    def test_site_offline_models2(self):
        self.assertIn("django_collect_offline", site_offline_models.site_models())

    def test_already_registered(self):
        self.assertRaises(
            AlreadyRegistered,
            site_offline_models.register,
            models=["django_collect_offline.testmodel"],
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
