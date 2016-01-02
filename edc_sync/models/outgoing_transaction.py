from django.db import models
from django.utils import timezone

from edc_base.model.constants import DEFAULT_BASE_FIELDS

from ..exceptions import SyncError

from .base_transaction import BaseTransaction
from .incoming_transaction import IncomingTransaction


class OutgoingTransaction(BaseTransaction):

    """ Transactions produced locally to be consumed/sent to a queue or consumer """
    is_consumed_middleman = models.BooleanField(
        default=False,
        db_index=True)

    is_consumed_server = models.BooleanField(
        default=False,
        db_index=True)

    using = models.CharField(max_length=25)

    objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.using:
            raise ValueError('Value for \'{}.using\' cannot be None.'.format(self._meta.model_name))
        if self.is_consumed_server and not self.consumed_datetime:
            self.consumed_datetime = timezone.now()
        super(OutgoingTransaction, self).save(*args, **kwargs)

    def copy_to_incoming_transaction(self, using):
        """Copies to IncomingTransaction on another DB.

        Note: this can also be done using the REST API"""
        if not self.is_consumed_server:
            if self.using == using:
                raise SyncError(
                    'Attempt to copy outgoing transaction to incoming transaction in same DB. '
                    'Got using={}'.format(using))
            options = {}
            for field in [field for field in IncomingTransaction._meta.fields]:
                try:
                    if field.name not in DEFAULT_BASE_FIELDS:
                        options.update({field.name: getattr(self, field.name)})
                except AttributeError:
                    pass
            IncomingTransaction.objects.using(using).create(**options)
            self.is_consumed_server = True
            self.save()

    class Meta:
        app_label = 'edc_sync'
        ordering = ['timestamp']
