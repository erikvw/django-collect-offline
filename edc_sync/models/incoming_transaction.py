import socket

from django.core import serializers
from django.db import models, transaction
from django.utils import timezone

from edc_device import Device

from ..exceptions import SyncError

from .base_transaction import BaseTransaction


class IncomingTransaction(BaseTransaction):

    """ Transactions received from a remote host. """

    check_hostname = None

    is_consumed = models.BooleanField(
        default=False)

    is_self = models.BooleanField(
        default=False)

    def deserialize_transaction(self, check_hostname=None, commit=True, check_device=True):
        device = Device()
        if check_device:
            if not device.is_server:
                raise SyncError('Objects may only be deserialized on a server. Got device={} {}.'.format(
                    device.device_role(device.device_id), device))
        inserted, updated, deleted = 0, 0, 0
        check_hostname = True if check_hostname is None else check_hostname
        for deserialized_object in serializers.deserialize(
                "json", self.aes_decrypt(self.tx), use_natural_foreign_keys=True, use_natural_primary_keys=True):
            if deserialized_object.object.hostname_modified == socket.gethostname() and check_hostname:
                raise SyncError('Incoming transactions exist that are from this host.')
            elif commit:
                if self.action == 'D':
                    deleted += self._deserialize_delete_tx(deserialized_object)
                elif self.action == 'I':
                    inserted += self._deserialize_insert_tx(deserialized_object)
                elif self.action == 'U':
                    updated += self._deserialize_update_tx(deserialized_object)
                else:
                    raise SyncError('Unexpected value for action. Got {}'.format(self.action))
                if any([inserted, deleted, updated]):
                    self.is_ignored = False
                    self.is_consumed = True
                    self.consumed_datetime = timezone.now()
                    self.consumer = '{}'.format(socket.gethostname())
                    self.save()
            else:
                return deserialized_object
        return inserted, updated, deleted

    def _deserialize_insert_tx(self, deserialized_object):
        with transaction.atomic():
            deserialized_object.save()
        return 1

    def _deserialize_update_tx(self, deserialized_object):
        return self._deserialize_insert_tx(deserialized_object)

    def _deserialize_delete_tx(self, deserialized_object, using):
        pass

    class Meta:
        app_label = 'edc_sync'
        ordering = ['timestamp', 'producer']
