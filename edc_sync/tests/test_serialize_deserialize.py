from django.test import TestCase

from ..models import OutgoingTransaction
from edc_sync.models.incoming_transaction import IncomingTransaction


class TestSerializeDeserialize(TestCase):

    def setUp(self):
        pass

    def test_serialization(self):
        instances = self.get_model_instances()
        for instance in instances:
            OutgoingTransaction.objects.all().delete()
            instance.save()
            self.assertTrue(OutgoingTransaction.objects.filter(tx_pk=instance.id,
                                                               action='U').exists())
            self.assertIsNotNone(OutgoingTransaction.objects.filter(tx_pk=instance.id,
                                 action='U').first().tx)

    def test_deserialization(self):
        instances = self.get_model_instances()
        for instance in instances:
            OutgoingTransaction.objects.all().delete()
            instance.save()
            outgoing = OutgoingTransaction.objects.get(tx_pk=instance.id,
                                                       action='U')
            outgoing.to_incoming_transaction('default')
            incoming = IncomingTransaction.objects.get(tx_pk=instance.id)
            obj = incoming.deserialize_transaction('default', check_hostname=False, commit=False)
            self.assertTrue(obj.object.id)

    def get_model_instances(self):
        """Override in concrete class to return a list of instances of models to be serialized and deserialized"""
        return []
