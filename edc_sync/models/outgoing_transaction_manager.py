from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone

from edc_base.model.constants import DEFAULT_BASE_FIELDS

from ..exceptions import SyncError

from ..models import IncomingTransaction


class CustomQuerySet(QuerySet):

    def copy_to_incoming_transaction(self, using):
        """Copies to IncomingTransaction on another DB.

        Note: this can also be done using the REST API"""
        for outgoing_transaction in self:
            if outgoing_transaction.is_consumed_server:
                raise SyncError(
                    'Filter by is_consumed_server=False before attempting to '
                    'copy transactions to IncomingTransaction.')
            if self._db == using:
                raise SyncError(
                    'Attempt to copy outgoing transaction to incoming transaction in same DB. '
                    'Got using={}'.format(using))
            options = {}
            for field in [field for field in IncomingTransaction._meta.fields]:
                try:
                    if field.name not in DEFAULT_BASE_FIELDS:
                        options.update({field.name: getattr(outgoing_transaction, field.name)})
                except AttributeError:
                    pass
            IncomingTransaction.objects.using(using).create(**options)
        self.update(is_consumed_server=True, consumed_datetime=timezone.now())


class OutgoingTransactionManager(models.Manager):

    def get_queryset(self):
        qs = CustomQuerySet(self.model)
        if self._db is not None:
            qs = qs.using(self._db)
        return qs
