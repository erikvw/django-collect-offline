from datetime import datetime

from django.core import serializers
from django.db.models import get_model

from edc.core.crypto_fields.classes import FieldCryptor

from .transaction_producer import transaction_producer


class SerializeToTransaction(object):

    def serialize(self, sender, instance, raw, created, using, **kwargs):

        """ Serializes the model instance to an encrypted json object
        and saves the json object to the OutgoingTransaction model.
        """
        if not raw:  # raw=True if you are deserializing
            try:
                if instance.is_serialized():
                    action = 'U'
                    if created:
                        action = 'I'
                    OutgoingTransaction = get_model('sync', 'OutgoingTransaction')
                    use_natural_keys = True if 'natural_key' in dir(sender) else False
                    if instance._meta.proxy_for_model:  # if this is a proxy model, get to the main model
                        instance = instance._meta.proxy_for_model.objects.using(using).get(id=instance.id)
                    json_tx = serializers.serialize("json", [instance, ], ensure_ascii=False,
                                                    use_natural_keys=use_natural_keys)
                    try:
                        # encrypt before saving to OutgoingTransaction
                        json_tx = FieldCryptor('aes', 'local').encrypt(json_tx)
                    except NameError:
                        pass
                    except AttributeError:
                        pass
                    return OutgoingTransaction.objects.using(using).create(
                        tx_name=instance._meta.object_name,
                        tx_pk=instance.id,
                        tx=json_tx,
                        timestamp=datetime.today().strftime('%Y%m%d%H%M%S%f'),
                        producer=transaction_producer,
                        action=action)
            except AttributeError as attribute_error:
                if 'is_serialized' in str(attribute_error):
                    pass
                else:
                    raise
