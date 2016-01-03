from django.db import models
from django.utils import timezone

from .base_transaction import BaseTransaction
from .outgoing_transaction_manager import OutgoingTransactionManager


class OutgoingTransaction(BaseTransaction):

    """ Transactions produced locally to be consumed/sent to a queue or consumer """
    is_consumed_middleman = models.BooleanField(
        default=False,
        db_index=True)

    is_consumed_server = models.BooleanField(
        default=False,
        db_index=True)

    using = models.CharField(max_length=25)

    objects = OutgoingTransactionManager()

    def save(self, *args, **kwargs):
        if not self.using:
            raise ValueError('Value for \'{}.using\' cannot be None.'.format(self._meta.model_name))
        if self.is_consumed_server and not self.consumed_datetime:
            self.consumed_datetime = timezone.now()
        super(OutgoingTransaction, self).save(*args, **kwargs)

    class Meta:
        app_label = 'edc_sync'
        ordering = ['timestamp']
