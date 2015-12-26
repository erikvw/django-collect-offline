from django.utils import timezone

from django.db import models

from ..mixins import TransactionMixin

from . import BaseTransaction


class IncomingTransaction(BaseTransaction, TransactionMixin):
    """ Transactions received from a remote producer and to be consumed locally. """
    is_consumed = models.BooleanField(
        default=False,
        db_index=True)

    def save(self, *args, **kwargs):
        if self.is_consumed and not self.consumed_datetime:
            self.consumed_datetime = timezone.now()
        super(IncomingTransaction, self).save(*args, **kwargs)

    class Meta:
        app_label = 'edc_sync'
        ordering = ['timestamp']
