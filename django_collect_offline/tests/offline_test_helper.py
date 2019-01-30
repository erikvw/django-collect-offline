import json

from django.apps import apps as django_apps
from django.core.exceptions import MultipleObjectsReturned
from edc_list_data.model_mixins import ListModelMixin
from unittest.case import TestCase

from ..models import OutgoingTransaction
from ..transaction import deserialize


class OfflineTestHelperError(Exception):
    pass


class OfflineTestHelper(TestCase):
    def offline_test_natural_key_attr(self, *app_labels, exclude_models=None):
        """Asserts all models in given apps have a
        natural_key model method.
        """
        exclude_models = exclude_models or []
        for app_label in app_labels:
            models = django_apps.get_app_config(app_label).get_models()
            for model in models:
                if (
                    model._meta.label_lower not in exclude_models
                    and not issubclass(model, ListModelMixin)
                    and ".tests." not in model.__module__
                ):
                    self.assertTrue(
                        "natural_key" in dir(model),
                        "Model method 'natural_key' missing. "
                        f"Got '{model._meta.label_lower}'.",
                    )

    def offline_test_get_by_natural_key_attr(self, *app_labels, exclude_models=None):
        """Asserts all models in given apps have a get_by_natural_key
        manager method.
        """
        exclude_models = exclude_models or []
        for app_label in app_labels:
            models = django_apps.get_app_config(app_label).get_models()
            for model in models:
                if (
                    model._meta.label_lower not in exclude_models
                    and not issubclass(model, ListModelMixin)
                    and ".tests." not in model.__module__
                ):
                    self.assertTrue(
                        "get_by_natural_key" in dir(model.objects),
                        f"Manager method 'get_by_natural_key' missing. "
                        f"Got '{model._meta.label_lower}'.",
                    )

    def offline_test_natural_keys(self, complete_required_crfs):
        """Asserts tuple from natural_key when passed to
        get_by_natural_key successfully gets the model instance.
        """
        for objs in complete_required_crfs.values():
            for obj in objs:
                options = obj.natural_key()
                try:
                    obj.__class__.objects.get_by_natural_key(*options)
                except obj.__class__.DoesNotExist:
                    self.fail(
                        f"get_by_natural_key query failed for "
                        f"'{obj._meta.label_lower}' with "
                        f"options {options}."
                    )
                except TypeError as e:
                    raise OfflineTestHelperError(
                        f"{e} See {obj._meta.label_lower}. Got {options}."
                    )

    def offline_test_natural_keys_by_schedule(self, visits=None, visit_attr=None):
        """A wrapper method for offline_test_natural_keys that uses
        the enrollment instance to test each CRF in each visit
        in the schedule linked to the enrollment model.
        """
        complete_required_crfs = {}
        for visit in visits:
            complete_required_crfs.update(
                {
                    visit.visit_code: self.complete_required_crfs(
                        visit_code=visit.visit_code,
                        visit=visit,
                        visit_attr=visit_attr,
                        subject_identifier=visit.subject_identifier,
                    )
                }
            )
        self.offline_test_natural_keys(complete_required_crfs)

    def offline_test_serializers_for_visit(self, complete_required_crfs):
        """Assert CRF model instances have transactions and that the
        transactions can be deserialized and compared to their original
        model instances.
        """
        for visit_code in [visit_code for visit_code in complete_required_crfs.keys()]:
            for obj in complete_required_crfs.get(visit_code):
                try:
                    outgoing_transaction = OutgoingTransaction.objects.get(
                        tx_name=obj._meta.label_lower, tx_pk=obj.pk
                    )
                    self.offline_test_deserialize(obj, outgoing_transaction)
                except MultipleObjectsReturned:
                    for outgoing_transaction in OutgoingTransaction.objects.filter(
                        tx_name=obj._meta.label_lower, tx_pk=obj.pk
                    ):
                        self.offline_test_deserialize(obj, outgoing_transaction)
                except OutgoingTransaction.DoesNotExist:
                    self.fail(
                        "OutgoingTransaction.DoesNotExist unexpectedly "
                        f"raised for {obj._meta.label_lower}"
                    )

    def offline_test_deserialize(self, obj, outgoing_transaction):
        """Assert object matches its deserialized transaction.
        """
        json_text = outgoing_transaction.aes_decrypt(outgoing_transaction.tx)
        for deserialised_obj in deserialize(json_text=json_text):
            json_tx = json.loads(json_text)[0]
            self.assertEqual(json_tx.get("model"), obj._meta.label_lower)
            # TODO: verify natural key values?
            self.assertEqual(obj.pk, deserialised_obj.object.pk)
