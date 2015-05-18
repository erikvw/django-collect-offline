import socket

from datetime import datetime

from django.db import models

from ..managers import IncomingTransactionManager

from .base_transaction import BaseTransaction


class IncomingTransaction(BaseTransaction):
    """ Transactions received from a remote producer and to be consumed locally. """
    is_consumed = models.BooleanField(
        default=False,
        db_index=True)

    is_self = models.BooleanField(
        default=False,
        db_index=True)

    objects = IncomingTransactionManager()

    def save(self, *args, **kwargs):
        if self.hostname_modified == socket.gethostname():
            self.is_self = True  # FIXME: is this needed?
        if self.is_consumed and not self.consumed_datetime:
            self.consumed_datetime = datetime.today()
        super(IncomingTransaction, self).save(*args, **kwargs)

    class Meta:
        app_label = 'sync'
        db_table = 'bhp_sync_incomingtransaction'
        ordering = ['timestamp']
