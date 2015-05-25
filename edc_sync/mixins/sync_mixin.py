import base64
import re

from datetime import datetime

from django.core import serializers
from django.apps import apps

from django_crypto_fields.classes import Cryptor
from django.core.exceptions import ImproperlyConfigured

from ..transaction_producer import transaction_producer


class SyncMixin(object):

    aes_mode = 'local'
    use_encryption = True

    def to_json(self, b64_encode=None):
        """Converts current instance to json, usually encrypted."""
        self.pk_is_uuid()
        use_natural_foreign_key = True if 'natural_key' in dir(self) else False
        json_tx = serializers.serialize(
            "json", [self, ],
            ensure_ascii=False,
            use_natural_foreign_keys=use_natural_foreign_key)
        if self.use_encryption:
            json_tx = Cryptor().aes_encrypt(json_tx, self.aes_mode)
        if b64_encode:
            return base64.b64encode(json_tx)
        return json_tx

    def pk_is_uuid(self):
        """Raises an exception if pk of current instance is not a UUID."""
        regex = re.compile('^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}\Z', re.I)
        if not regex.match(str(self.pk)):
            raise ImproperlyConfigured('Sync failed. Expected pk to be a UUID. Got pk=\'{}\''.format(self.pk))

    def action(self, created=None, deleted=None):
        if created:
            return 'I'
        elif deleted:
            return 'D'
        else:
            return 'U'

    def to_outgoing(self, created=None, deleted=None, using=None):
        """Saves the current instance to the OutgoingTransaction model."""
        OutgoingTransaction = apps.get_model('edc_sync.OutgoingTransaction')
        return OutgoingTransaction.objects.using(using).create(
            tx_name=self._meta.object_name,
            tx_modified=self.modified,
            tx_pk=self.id,
            tx=self.to_json(b64_encode=True),
            timestamp=datetime.today().strftime('%Y%m%d%H%M%S%f'),
            producer=transaction_producer,
            action=self.action(created=created, deleted=deleted))

    def to_inspector(self):
        pass
