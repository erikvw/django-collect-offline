from datetime import datetime

from django.core import serializers
from django.apps import apps

from django_crypto_fields.classes import Cryptor

from sync_old import SyncError

from sync_old import transaction_producer


class Transaction(object):

    def __init__(self, model_instance, using, aes_mode=None):
        self.aes_mode = aes_mode or 'local'
        self.model_instance = model_instance
        try:
            if not self.model_instance.is_serialized():
                raise SyncError('Model is not flagged for synchronization.')
        except AttributeError:
            raise SyncError('Model is not configured for synchronization.')
        if self.model_instance._meta.proxy_for_model:
            self.model_instance = self.model_instance._meta.proxy_for_model.objects.using(
                self.using).get(id=self.model_instance.id)
        self.using = using

    def to_json(self, encrypt=None):
        encrypt = True if encrypt is None else encrypt
        use_natural_foreign_key = True if 'natural_key' in dir(self.model_instance) else False
        json_tx = serializers.serialize(
            "json", [self.model_instance, ],
            ensure_ascii=False,
            use_natural_foreign_keys=use_natural_foreign_key)
        if encrypt:
            json_tx = Cryptor().aes_encrypt(json_tx, self.aes_mode)
        return json_tx

    def to_outgoing(self, action, using=None, encrypt=None):
        using = self.using if using is None else using
        encrypt = True if encrypt is None else encrypt
        OutgoingTransaction = apps.get_model('sync_old', 'OutgoingTransaction')
        OutgoingTransaction.objects.using(using).create(
            tx_name=self.model_instance._meta.object_name,
            tx_pk=self.model_instance.id,
            tx=self.to_json(),
            timestamp=datetime.today().strftime('%Y%m%d%H%M%S%f'),
            producer=transaction_producer,
            action=action)

