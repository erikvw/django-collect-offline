import socket

from django.core import serializers
from django.db import models, transaction
from django.utils import timezone

from edc_base.encrypted_fields import FieldCryptor

from ..exceptions import SyncError

from .base_transaction import BaseTransaction
from .incoming_transaction_manager import IncomingTransactionManager
from .transaction_producer import transaction_producer


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

    def deserialize_transaction(self, using, check_hostname=None):
        inserted, updated, deleted = 0, 0, 0
        check_hostname = True if check_hostname is None else check_hostname
        decrypted_transaction = FieldCryptor('aes', 'local').decrypt(self.tx)
        for obj in serializers.deserialize("json", decrypted_transaction):
            if self.action == 'D':
                deleted = self.deserialize_delete_tx(obj, using, check_hostname)
            elif self.action == 'I':
                inserted = self.deserialize_insert_tx(obj, using, check_hostname)
            elif self.action == 'U':
                updated = self.deserialize_update_tx(obj, using, check_hostname)
            else:
                raise SyncError('Unexpected value for action. Got {}'.format(self.action))
            if any([inserted, deleted, updated]):
                self.is_ignored = False
                self.is_consumed = True
                self.consumed_datetime = timezone.now()
                self.consumer = transaction_producer
                self.save(using=using)
        return inserted, updated, deleted

    def deserialize_insert_tx(self, obj, using, check_hostname=None, verbose=None):
        return self.deserialize_update_tx(obj, using, check_hostname, verbose)

    def deserialize_delete_tx(self, obj, using, check_hostname=None):
        # obj.object.deserialize_prep(action='D')
        count = 0
        check_hostname = True if check_hostname is None else check_hostname
        if obj.object.hostname_modified == socket.gethostname() and check_hostname:
            raise SyncError('Incoming transactions exist that are from this host.')
        else:
            with transaction.atomic(using=using):
                self.is_ignored = False
                self.is_consumed = True
                self.consumer = transaction_producer
                self.save(using=using)
                count = 1
        return count

    def deserialize_update_tx(self, obj, using, check_hostname=None, verbose=None):
        count = 0
        check_hostname = True if check_hostname is None else check_hostname
        if obj.object.hostname_modified == socket.gethostname() and check_hostname:
            raise SyncError('Incoming transactions exist that are from this host.')
        else:
            with transaction.atomic(using):
                obj.save(using=using)
                count = 1
        return count

    class Meta:
        app_label = 'edc_sync'
        # db_table = 'bhp_sync_incomingtransaction'
        ordering = ['timestamp', 'producer']
