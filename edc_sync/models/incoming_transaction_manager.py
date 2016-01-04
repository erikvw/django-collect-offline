from collections import namedtuple

from django.db import models
from django.db.models.query import QuerySet

from edc_device import Device

from ..exceptions import SyncError

MessageTuple = namedtuple('Message', 'index, total, inserted updated deleted producer tx_name tx_pk success')


class CustomQuerySet(QuerySet):

    def deserialize(self, check_hostname=None, ignore_device_id=None, custom_device=None):
        """Deserialize new incoming transactions."""
        device = custom_device or Device()
        check_hostname = True if check_hostname is None else check_hostname
        if not device.is_server:
            if not ignore_device_id:
                raise SyncError('Transactions can only be deserialized on a host that is a server. '
                                'Got device id {}'.format(device.device_id))
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
        qs = CustomQuerySet(self.model)
        if self._db is not None:
            qs = qs.using(self._db)
        return qs
