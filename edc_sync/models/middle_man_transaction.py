import json

from django.conf import settings
from django.db import models
from django.db.models import get_model
from django.utils import timezone

from edc_device import device
from edc_base.encrypted_fields import FieldCryptor

from ..exceptions import SyncError

from .base_transaction import BaseTransaction


class MiddleManTransaction(BaseTransaction):

    """A model class for transactions produced locally to be consumed/sent
    to a queue or consumer """

    is_consumed_middleman = models.BooleanField(
        default=False,
        db_index=True)

    is_consumed_server = models.BooleanField(
        default=False,
        db_index=True)

    def save(self, *args, **kwargs):
        if self.is_consumed_server and not self.consumed_datetime:
            self.consumed_datetime = timezone.now()
        if not device.is_middleman:
            raise SyncError(
                '\'{0}\' is not configured to be a Middleman. '
                'Transaction cannot be created.'.format(settings.DEVICE_ID))
        super(MiddleManTransaction, self).save(*args, **kwargs)

    def decrypt_transaction(self):
            model_dict = FieldCryptor('aes', 'local').decrypt(self.tx)
            return json.loads(model_dict)

    def deserialize_to_inspector_on_post_save(self, instance, raw, created, using, **kwargs):
        model_dict = self.decrypt_transaction(self)[0]
        model = get_model(model_dict.get('model').split('.'))
        try:
            model().save_to_inspector(
                model_dict.get('fields'),
                model_dict.get('pk'),
                using)
        except AttributeError as e:
            if 'save_to_inspector' not in str(e):
                raise SyncError(str(e))

    objects = models.Manager()

    class Meta:
        app_label = 'edc_sync'
        ordering = ['timestamp']
