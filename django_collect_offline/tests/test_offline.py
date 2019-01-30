from django.core.exceptions import MultipleObjectsReturned
from django.test import TestCase, tag
from django.test.utils import override_settings

from ..constants import INSERT, UPDATE
from ..models import OutgoingTransaction
from ..offline_model import OfflineGetByNaturalKeyMissing
from ..offline_model import OfflineHistoricalManagerError
from ..offline_model import OfflineModel
from ..offline_model import OfflineNaturalKeyMissing
from ..offline_model import OfflineUuidPrimaryKeyMissing
from ..site_offline_models import site_offline_models
from .models import TestModel, BadTestModel, AnotherBadTestModel, YetAnotherBadTestModel
from .models import TestModelWithFkProtected
from .models import TestOfflineModelNoHistoryManager, TestOfflineModelNoUuid


class TestOffline(TestCase):

    multi_db = True

    def setUp(self):
        site_offline_models.registry = {}
        site_offline_models.loaded = False
        offline_models = [
            "django_collect_offline.testmodel",
            "django_collect_offline.badtestmodel",
            "django_collect_offline.anotherbadtestmodel",
            "django_collect_offline.yetanotherbadtestmodel",
            "django_collect_offline.testmodelwithfkprotected",
            "django_collect_offline.testmodelwithm2m",
            "django_collect_offline.testofflinemodelnohistorymanager",
            "django_collect_offline.testofflinemodelnouuid",
        ]
        site_offline_models.register(models=offline_models)

    def get_credentials(self):
        return self.create_apikey(username=self.username, api_key=self.api_client_key)

    def test_str(self):
        obj = TestModel()
        obj = OfflineModel(obj)
        self.assertTrue(str(obj))
        self.assertTrue(repr(obj))

    def test_raises_on_missing_natural_key(self):
        with override_settings(DEVICE_ID="10"):
            with self.assertRaises(OfflineNaturalKeyMissing):
                BadTestModel.objects.using("client").create()

    def test_raises_on_missing_get_by_natural_key(self):
        with override_settings(DEVICE_ID="10"):
            with self.assertRaises(OfflineGetByNaturalKeyMissing):
                AnotherBadTestModel.objects.using("client").create()

    def test_raises_on_wrong_type_of_historical_manager(self):
        with override_settings(DEVICE_ID="10"):
            with self.assertRaises(OfflineHistoricalManagerError):
                YetAnotherBadTestModel.objects.using("client").create()

    def test_raises_on_no_historical_manager(self):
        with override_settings(DEVICE_ID="10"):
            try:
                TestOfflineModelNoHistoryManager.objects.using("client").create()
            except OfflineHistoricalManagerError:
                self.fail("OfflineHistoricalManagerError unexpectedly raised.")

    def test_raises_on_missing_uuid_primary_key(self):
        with override_settings(DEVICE_ID="10"):
            with self.assertRaises(OfflineUuidPrimaryKeyMissing):
                TestOfflineModelNoUuid.objects.using("client").create()

    def test_creates_outgoing_on_add(self):
        with override_settings(DEVICE_ID="10"):
            test_model = TestModel.objects.using("client").create(f1="erik")
            with self.assertRaises(OutgoingTransaction.DoesNotExist):
                try:
                    OutgoingTransaction.objects.using("client").get(
                        tx_pk=test_model.pk,
                        tx_name="django_collect_offline.testmodel",
                        action=INSERT,
                    )
                except OutgoingTransaction.DoesNotExist:
                    pass
                else:
                    raise OutgoingTransaction.DoesNotExist()
            history_obj = test_model.history.using("client").get(id=test_model.id)
            with self.assertRaises(OutgoingTransaction.DoesNotExist):
                try:
                    OutgoingTransaction.objects.using("client").get(
                        tx_pk=history_obj.history_id,
                        tx_name="django_collect_offline.historicaltestmodel",
                        action=INSERT,
                    )
                except OutgoingTransaction.DoesNotExist:
                    pass
                else:
                    raise OutgoingTransaction.DoesNotExist()

    def test_creates_outgoing_on_add_with_fk_in_order(self):
        with override_settings(DEVICE_ID="10"):
            outgoing = {}
            test_model = TestModel.objects.using("client").create(f1="erik")
            test_model_with_fk = TestModelWithFkProtected.objects.using(
                "client"
            ).create(f1="f1", test_model=test_model)
            outgoing.update(
                test_model=OutgoingTransaction.objects.using("client").get(
                    tx_pk=test_model.pk,
                    tx_name="django_collect_offline.testmodel",
                    action=INSERT,
                )
            )
            history_obj = test_model.history.using("client").get(id=test_model.id)
            outgoing.update(
                test_model_historical=OutgoingTransaction.objects.using("client").get(
                    tx_pk=history_obj.history_id,
                    tx_name="django_collect_offline.historicaltestmodel",
                    action=INSERT,
                )
            )

            with self.assertRaises(OutgoingTransaction.DoesNotExist):
                try:
                    outgoing.update(
                        test_model_with_fk=OutgoingTransaction.objects.using(
                            "client"
                        ).get(
                            tx_pk=test_model_with_fk.pk,
                            tx_name="django_collect_offline.testmodelwithfkprotected",
                            action=INSERT,
                        )
                    )
                except OutgoingTransaction.DoesNotExist:
                    pass
                else:
                    raise OutgoingTransaction.DoesNotExist()
            history_obj = test_model_with_fk.history.using("client").get(
                id=test_model_with_fk.id
            )
            with self.assertRaises(OutgoingTransaction.DoesNotExist):
                try:
                    outgoing.update(
                        test_model_with_fk_historical=(
                            OutgoingTransaction.objects.using("client").get(
                                tx_pk=history_obj.history_id,
                                tx_name=(
                                    "django_collect_offline.historicaltest"
                                    "modelwithfkprotected"
                                ),
                                action=INSERT,
                            )
                        )
                    )
                except OutgoingTransaction.DoesNotExist:
                    pass
                else:
                    raise OutgoingTransaction.DoesNotExist()

    @override_settings(ALLOW_MODEL_SERIALIZATION=False)
    def test_does_not_create_outgoing(self):
        with override_settings(DEVICE_ID="10", ALLOW_MODEL_SERIALIZATION=False):
            test_model = TestModel.objects.using("client").create(f1="erik")
            with self.assertRaises(OutgoingTransaction.DoesNotExist):
                OutgoingTransaction.objects.using("client").get(tx_pk=test_model.pk)

    def test_creates_outgoing_on_change(self):
        with override_settings(DEVICE_ID="10"):
            test_model = TestModel.objects.using("client").create(f1="erik")
            test_model.save(using="client")
            with self.assertRaises(OutgoingTransaction.DoesNotExist):
                try:
                    OutgoingTransaction.objects.using("client").get(
                        tx_pk=test_model.pk,
                        tx_name="django_collect_offline.testmodel",
                        action=INSERT,
                    )
                    OutgoingTransaction.objects.using("client").get(
                        tx_pk=test_model.pk,
                        tx_name="django_collect_offline.testmodel",
                        action=UPDATE,
                    )
                except OutgoingTransaction.DoesNotExist:
                    pass
                else:
                    raise OutgoingTransaction.DoesNotExist()
            self.assertEqual(
                2,
                OutgoingTransaction.objects.using("client")
                .filter(
                    tx_name="django_collect_offline.historicaltestmodel", action=INSERT
                )
                .count(),
            )

    def test_timestamp_is_default_order(self):
        with override_settings(DEVICE_ID="10"):
            test_model = TestModel.objects.using("client").create(f1="erik")
            test_model.save(using="client")
            last = 0
            for obj in OutgoingTransaction.objects.using("client").all():
                self.assertGreaterEqual(int(obj.timestamp), last)
                last = int(obj.timestamp)

    def test_created_obj_serializes_to_correct_db(self):
        """Asserts that the obj and the audit obj serialize to the
        correct DB in a multi-database environment.
        """
        TestModel.objects.using("client").create(f1="erik")
        result = [
            obj.tx_name for obj in OutgoingTransaction.objects.using("client").all()
        ]
        result.sort()
        self.assertListEqual(
            result,
            [
                "django_collect_offline.historicaltestmodel",
                "django_collect_offline.testmodel",
            ],
        )
        self.assertListEqual(
            [obj.tx_name for obj in OutgoingTransaction.objects.using("server").all()],
            [],
        )
        self.assertRaises(
            OutgoingTransaction.DoesNotExist,
            OutgoingTransaction.objects.using("server").get,
            tx_name="django_collect_offline.testmodel",
        )
        self.assertRaises(
            MultipleObjectsReturned,
            OutgoingTransaction.objects.using("client").get,
            tx_name__contains="testmodel",
        )

    def test_updated_obj_serializes_to_correct_db(self):
        """Asserts that the obj and the audit obj serialize to the
        correct DB in a multi-database environment.
        """
        test_model = TestModel.objects.using("client").create(f1="erik")
        result = [
            obj.tx_name
            for obj in OutgoingTransaction.objects.using("client").filter(action=INSERT)
        ]
        result.sort()
        self.assertListEqual(
            result,
            [
                "django_collect_offline.historicaltestmodel",
                "django_collect_offline.testmodel",
            ],
        )
        self.assertListEqual(
            [
                obj.tx_name
                for obj in OutgoingTransaction.objects.using("client").filter(
                    action=UPDATE
                )
            ],
            [],
        )
        test_model.save(using="client")
        self.assertListEqual(
            [
                obj.tx_name
                for obj in OutgoingTransaction.objects.using("client").filter(
                    action=UPDATE
                )
            ],
            ["django_collect_offline.testmodel"],
        )
        result = [
            obj.tx_name
            for obj in OutgoingTransaction.objects.using("client").filter(action=INSERT)
        ]
        result.sort()
        self.assertListEqual(
            result,
            [
                "django_collect_offline.historicaltestmodel",
                "django_collect_offline.historicaltestmodel",
                "django_collect_offline.testmodel",
            ],
        )
