from datetime import datetime

from django.core import serializers
from django.apps import apps

# from edc.core.crypto_fields.classes import FieldCryptor
from django_crypto_fields.classes import Cryptor

from sync_old import transaction_producer


class SerializeToTransaction(object):

    def serialize(self, sender, instance, raw, created, using, **kwargs):
        """ Serializes the model instance to an encrypted json object
        and saves the json object to the OutgoingTransaction model.
        """
        if not raw:  # raw=True if you are deserializing
            try:
                is_serialized = instance.is_serialized()
            except AttributeError:
                pass
            if is_serialized:
                action = 'U'
                if created:
                    action = 'I'
                OutgoingTransaction = apps.get_model('sync_old', 'OutgoingTransaction')
                use_natural_keys = True if 'natural_key' in dir(sender) else False
                # if this is a proxy model, get to the main model
                if instance._meta.proxy_for_model:
                    instance = instance._meta.proxy_for_model.objects.using(using).get(id=instance.id)
                json_tx = serializers.serialize(
                    "json", [instance, ],
                    ensure_ascii=False,
                    use_natural_keys=use_natural_keys)
                json_tx = Cryptor().aes_encrypt(json_tx, 'local')
                return OutgoingTransaction.objects.using(using).create(
                    tx_name=instance._meta.object_name,
                    tx_pk=instance.id,
                    tx=json_tx,
                    timestamp=datetime.today().strftime('%Y%m%d%H%M%S%f'),
                    producer=transaction_producer,
                    action=action)
