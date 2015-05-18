from datetime import datetime

from django.db import models

from .base_transaction import BaseTransaction


class OutgoingTransaction(BaseTransaction):

    """ Transactions produced locally to be consumed/sent to a queue or consumer """
    is_consumed_middleman = models.BooleanField(
        default=False,
        db_index=True,
    )

    is_consumed_server = models.BooleanField(
        default=False,
        db_index=True,
    )

    objects = models.Manager()

    def save(self, *args, **kwargs):
        if self.is_consumed_server and not self.consumed_datetime:
            self.consumed_datetime = datetime.today()
        super(OutgoingTransaction, self).save(*args, **kwargs)

    class Meta:
        app_label = 'sync'
        db_table = 'bhp_sync_outgoingtransaction'
        ordering = ['timestamp']
