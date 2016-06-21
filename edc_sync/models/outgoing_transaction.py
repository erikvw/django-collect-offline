from django.db import models
from django.utils import timezone


from edc_base.model.constants import DEFAULT_BASE_FIELDS

from ..exceptions import SyncError

from .base_transaction import BaseTransaction
from .incoming_transaction import IncomingTransaction
from .outgoing_transaction_manager import OutgoingTransactionManager


class OutgoingTransaction(BaseTransaction):

    """ Transactions produced locally to be consumed/sent to a queue or consumer. """

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

    def to_incoming_transaction(self, using):
        """Copies self to the IncomingTransaction model on database \'using\'.

        Note: making sure the transaction is not copied back to incoming in the same
        DB is the callers responsibility. See OutgoingTransactionManager.
        """
        if self.is_consumed_server:
            raise SyncError(
                'Filter by is_consumed_server=False before attempting to '
                'copy transactions to IncomingTransaction.')
        if self.is_error:
            raise SyncError(
                'Filter by is_error=False before attempting to '
                'copy transactions to IncomingTransaction.')
        options = {}
        for field in [field for field in IncomingTransaction._meta.fields]:
            try:
                if field.name not in DEFAULT_BASE_FIELDS:
                    options.update({field.name: getattr(self, field.name)})
            except AttributeError:
                pass
        try:
            obj = IncomingTransaction.objects.using(using).get(id=self.id)
        except IncomingTransaction.DoesNotExist:
            obj = IncomingTransaction.objects.using(using).create(**options)
        return obj

    class Meta:
        app_label = 'edc_sync'
        ordering = ['timestamp']
