from datetime import datetime

from django.db import models

from . import BaseTransaction


class OutgoingTransaction(BaseTransaction):
    """A model class for locally created transactions ready to be fetched
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

    # objects = models.Manager()

    def save(self, *args, **kwargs):
        if self.is_consumed_server and not self.consumed_datetime:
            self.consumed_datetime = datetime.today()
        super(OutgoingTransaction, self).save(*args, **kwargs)

    class Meta:
        app_label = 'edc_sync'
        ordering = ['timestamp']
