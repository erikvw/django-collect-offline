import json

from django.apps import apps as django_apps
from django.core import serializers
from django.core.exceptions import MultipleObjectsReturned

from edc_sync.models import OutgoingTransaction


class SyncTestError(Exception):
    pass


class SyncTestSerializerMixin:

    def sync_test_natural_key_attr(self, *app_labels):
        """Asserts all models in given apps have a natural_key method"""
        for app_label in app_labels:
            models = django_apps.get_app_config(app_label).get_models()
            for model in models:
                self.assertTrue(
                    'natural_key' in dir(model),
                    'Model method \'natural_key\' missing. Got \'{}\'.'.format(
                        model._meta.label_lower))

    def sync_test_get_by_natural_key_attr(self, *app_labels):
        """Asserts all models in given apps have a natural_key method"""
        for app_label in app_labels:
            models = django_apps.get_app_config(app_label).get_models()
            for model in models:
                self.assertTrue(
                    'get_by_natural_key' in dir(model.objects),
                    'Manager method \'get_by_natural_key\' missing. Got \'{}\'.'.format(
                        model._meta.label_lower))

    def sync_test_natural_keys(self, complete_required_crfs, verbose=None):
        for objs in complete_required_crfs.values():
            for obj in objs:
                if verbose:
                    print(obj._meta.label_lower)
                options = obj.natural_key()
                try:
                    obj.__class__.objects.get_by_natural_key(*options)
                except obj.__class__.DoesNotExist:
                    self.fail(
                        'get_by_natural_key query failed for \'{}\' with options {}.'.format(
                            obj._meta.label_lower, options))
                except TypeError as e:
                    raise SyncTestError('{} See {}. Got {}.'.format(str(e), obj._meta.label_lower, options))

    def sync_test_natural_keys_by_schedule(self, enrollment, verbose=True):
        """A wrapper method for sync_test_natural_keys that uses the enrollment instance
        to test each CRF in each visit in the schedule linked to the enrollment model."""
        for visit in enrollment.schedule.visits:
            if verbose:
                print(visit.code)
            complete_required_crfs = self.complete_required_crfs(visit.code)
            self.sync_test_natural_keys(complete_required_crfs, verbose=verbose)

    def sync_test_serializers_for_visit(self, complete_required_crfs, verbose=None):
        """Assert CRF model instances have transactions and that the
        transactions can be deserialized and compared to their original
        model instances."""
        for obj in complete_required_crfs:
            try:
                outgoing_transaction = OutgoingTransaction.objects.get(
                    tx_name=obj._meta.label_lower,
                    tx_pk=obj.pk)
                self.sync_test_deserialize(obj, outgoing_transaction, verbose=verbose)
            except MultipleObjectsReturned:
                for outgoing_transaction in OutgoingTransaction.objects.filter(
                        tx_name=obj._meta.label_lower, tx_pk=obj.pk):
                    self.sync_test_deserialize(obj, outgoing_transaction, verbose=verbose)
            except OutgoingTransaction.DoesNotExist:
                self.fail(
                    'OutgoingTransaction.DoesNotExist unexpectedly '
                    'raised for {}'.format(obj._meta.label_lower))

    def sync_test_deserialize(self, obj, outgoing_transaction, verbose=None):
        """Assert object matches its deserialized transaction."""
        tx = outgoing_transaction.aes_decrypt(outgoing_transaction.tx)
        for deserialised_obj in serializers.deserialize(
                "json", tx, use_natural_foreign_keys=True, use_natural_primary_keys=True):
            json_tx = json.loads(tx)[0]
            self.assertEqual(json_tx.get('model'), obj._meta.label_lower)
            # TODO: verify natural key values?
            self.assertEqual(obj.pk, deserialised_obj.object.pk)
            if verbose:
                print(obj._meta.label_lower)
