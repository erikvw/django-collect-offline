from datetime import datetime

from django.core import serializers
from django.apps import apps

from django_crypto_fields.classes import Cryptor

from .. import transaction_producer


class SyncMixin(object):

    aes_mode = 'local'
    use_encryption = True

    def to_json(self):
        """Converts current instance to json, usually encrypted."""
        use_natural_foreign_key = True if 'natural_key' in dir(self) else False
        json_tx = serializers.serialize(
            "json", [self, ],
            ensure_ascii=False,
            use_natural_foreign_keys=use_natural_foreign_key)
        if self.use_encryption:
            json_tx = Cryptor().aes_encrypt(json_tx, self.aes_mode)
        return json_tx

    def action(self, created=None, deleted=None):
        if created is True:
            return 'I'
        if created is False:
            return 'U'
        if deleted is True:
            return 'D'

    def to_outgoing(self, action, using=None):
        """Saves the current instance to the OutgoingTransaction model."""
        OutgoingTransaction = apps.get_model('edc_sync.OutgoingTransaction')
        return OutgoingTransaction.objects.using(using).create(
            tx_name=self._meta.object_name,
            tx_pk=self.id,
            tx=self.to_json(),
            timestamp=datetime.today().strftime('%Y%m%d%H%M%S%f'),
            producer=transaction_producer,
            action=action)

    def to_inspector(self):
        pass
