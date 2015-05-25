from django.db import models
from django.utils import timezone

from . import BaseTransaction


class OutgoingTransaction(BaseTransaction):
    """A model class for locally created serialized transactions ready to be fetched
    by another system."""
    is_consumed = models.BooleanField(
        default=False,
        db_index=True)

    is_consumed_middleman = models.BooleanField(
        default=False,
        db_index=True,
    )

    is_consumed_server = models.BooleanField(
        default=False,
        db_index=True,
    )

    def __repr__(self):
        return '{0}({{\'tx_pk\': \'{1}\',\'tx_name\': \'{2}\', \'action\': \'{3}\'}})'.format(
            self.__class__.__name__, self.tx_pk, self.tx_name, self.action)

    def __str__(self):
        return '{}:{}:{}'.format(self.action, self.tx_name, self.tx_pk)

    def save(self, *args, **kwargs):
        if self.is_consumed_server and not self.consumed_datetime:
            self.consumed_datetime = timezone.now()
        super(OutgoingTransaction, self).save(*args, **kwargs)

    class Meta:
        app_label = 'edc_sync'
        ordering = ['timestamp']
        unique_together = ('tx_name', 'tx_pk', 'tx_modified')
