import socket

from django.core import serializers
from django.db import models, transaction
from django.utils import timezone
from django_crypto_fields.cryptor import Cryptor

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

    # objects = IncomingTransactionManager()

    def deserialize_transaction(self, using, check_hostname=None, commit=True, check_device=True):
        device = Device()
        if check_device:
            if not device.is_server:
                raise SyncError('Objects may only be deserialized on a server. Got device={} {}.'.format(
                    device.device_role(device.device_id), device))
        if using != 'default':
            # get_by_natural_key only works on default
            raise SyncError('Deserialization target database key must be \'default\' '
                            '(Client->Server). Got \'{}\''.format(using))
        inserted, updated, deleted = 0, 0, 0
        check_hostname = True if check_hostname is None else check_hostname
        decrypted_transaction = Cryptor().aes_decrypt(self.tx, 'local')
        for deserialized_object in serializers.deserialize(
                "json", decrypted_transaction, use_natural_foreign_keys=True, use_natural_primary_keys=True):
            if deserialized_object.object.hostname_modified == socket.gethostname() and check_hostname:
                raise SyncError('Incoming transactions exist that are from this host.')
            elif commit:
                if self.action == 'D':
                    deleted += self.deserialize_delete_tx(deserialized_object, using)
                elif self.action == 'I':
                    inserted += self.deserialize_insert_tx(deserialized_object, using)
                elif self.action == 'U':
                    updated += self.deserialize_update_tx(deserialized_object, using)
                else:
                    raise SyncError('Unexpected value for action. Got {}'.format(self.action))
                if any([inserted, deleted, updated]):
                    self.is_ignored = False
                    self.is_consumed = True
                    self.consumed_datetime = timezone.now()
                    self.consumer = '{}-{}'.format(socket.gethostname(), using)
                    self.save(using=using)
            else:
                return deserialized_object
        return inserted, updated, deleted

    def deserialize_insert_tx(self, deserialized_object, using):
        with transaction.atomic(using):
            deserialized_object.save(using=using)
        return 1

    def deserialize_update_tx(self, deserialized_object, using):
        return self.deserialize_insert_tx(deserialized_object, using)

    def deserialize_delete_tx(self, deserialized_object, using):
        pass

    class Meta:
        app_label = 'edc_sync'
        ordering = ['timestamp', 'producer']
