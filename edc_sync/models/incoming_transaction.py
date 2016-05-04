import socket

from django.core import serializers
from django.db import models, transaction
from django.utils import timezone
from django_crypto_fields.classes import FieldCryptor

from edc_device import Device

from ..exceptions import SyncError

from .base_transaction import BaseTransaction
from .incoming_transaction_manager import IncomingTransactionManager


class IncomingTransaction(BaseTransaction):
    """ Transactions received from a remote producer and to be consumed locally. """

    check_hostname = None

    is_consumed = models.BooleanField(
        default=False,
        db_index=True)

    is_self = models.BooleanField(
        default=False,
        db_index=True)

    objects = IncomingTransactionManager()

    def deserialize_transaction(self, using, check_hostname=None, commit=True):
        device = Device()
        if not device.is_server:
            raise SyncError('Objects may only be deserialized on a server. Got device={} {}.'.format(
                device.device_role(device.device_id), device))
        if using != 'default':
            # get_by_natural_key onl works on default
            raise SyncError('Server database key must be \'default\'. Got \'{}\''.format(using))
        inserted, updated, deleted = 0, 0, 0
        check_hostname = True if check_hostname is None else check_hostname
        decrypted_transaction = FieldCryptor('aes', 'local').decrypt(self.tx)
        for obj in serializers.deserialize("json", decrypted_transaction):
            if obj.object.hostname_modified == socket.gethostname() and check_hostname:
                raise SyncError('Incoming transactions exist that are from this host.')
            elif commit:
                if self.action == 'D':
                    deleted = self.deserialize_delete_tx(obj, using)
                elif self.action == 'I':
                    inserted = self.deserialize_insert_tx(obj, using)
                elif self.action == 'U':
                    updated = self.deserialize_update_tx(obj, using)
                else:
                    raise SyncError('Unexpected value for action. Got {}'.format(self.action))
                if any([inserted, deleted, updated]):
                    self.is_ignored = False
                    self.is_consumed = True
                    self.consumed_datetime = timezone.now()
                    self.consumer = '{}-{}'.format(socket.gethostname(), using)
                    self.save(using=using)
            else:
                return obj
        return inserted, updated, deleted

    def deserialize_insert_tx(self, obj, using):
        with transaction.atomic(using):
            obj.save(using=using)
        return 1

    def deserialize_update_tx(self, obj, using):
        return self.deserialize_insert_tx(obj, using)

    def deserialize_delete_tx(self, obj, using):
        pass

    class Meta:
        app_label = 'edc_sync'
        ordering = ['timestamp', 'producer']
