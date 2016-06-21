from collections import namedtuple

from django.db import models
from django.db.models.query import QuerySet

from edc_device import Device

from ..exceptions import SyncError

MessageTuple = namedtuple('Message', 'index, total, inserted updated deleted producer tx_name tx_pk success')


class IncomingTransactionQuerySet(QuerySet):

    def deserialize(self, check_hostname=None):
        """Deserialize all objects in the queryset.

        Since 'get_by_natural_key' assumes using='default', this may only
        be called on a server where the database is \'default\'.
        """
        device = Device()
        check_hostname = True if check_hostname is None else check_hostname
        if not device.is_server:
            raise SyncError('Objects may only be deserialized on a server. '
                            'Got device=\'{}\' \'{}\'.'.format(
                                device.device_role(device.device_id), device))
        if self._db != 'default':
            raise SyncError('Server database key may only be \'default\'. Got \'{}\''.format(self._db))
        total = self.count()
        messages = []
        for index, incoming_transaction in enumerate(self):
            inserted, updated, deleted = incoming_transaction.deserialize_transaction(
                using=self._db, check_hostname=check_hostname)
            messages.append(MessageTuple(
                index, total, inserted, updated, deleted,
                incoming_transaction.producer,
                incoming_transaction.tx_name,
                incoming_transaction.tx_pk,
                True))
        return messages


class IncomingTransactionManager(models.Manager):

    def get_queryset(self):
        qs = IncomingTransactionQuerySet(self.model)
        if self._db is not None:
            qs = qs.using(self._db)
        return qs
