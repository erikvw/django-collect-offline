from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone

from edc_sync.exceptions import SyncError


# class CustomQuerySet(QuerySet):
# 
#     def copy_to_incoming_transaction(self, using):
#         """Copies to IncomingTransaction on another DB.
# 
#         Note: this can also be done using the REST API"""
#         if self._db == using:
#             raise SyncError(
#                 'Attempt to copy outgoing transaction to incoming transaction in same DB. '
#                 'Got using={}'.format(using))
#         for outgoing_transaction in self:
#             outgoing_transaction.to_incoming_transaction(using)
#         self.using(self._db).update(is_consumed_server=True, consumed_datetime=timezone.now())
# 
# 
# class OutgoingTransactionManager(models.Manager):
# 
#     def get_queryset(self):
#         qs = CustomQuerySet(self.model)
#         if self._db is not None:
#             qs = qs.using(self._db)
#         return qs
