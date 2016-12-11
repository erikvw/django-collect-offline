import json

from django.core import serializers
from django.core.exceptions import MultipleObjectsReturned

from edc_sync.models import OutgoingTransaction


class SyncTestSerializerMixin:

    def sync_test_serializers_for_visit(self, complete_required_crfs, verbose=None):
        """Assert CRF model instances have transactions and that the transactions can be deserialized and compared
        to their original model instances."""
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
                    'OutgoingTransaction.DoesNotExist unexpectedly raised for {}'.format(obj._meta.label_lower))

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
