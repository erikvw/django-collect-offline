from collections import namedtuple
from datetime import timedelta

from django.db import models
from django.utils import timezone

from edc_base.encrypted_fields import FieldCryptor
from edc_device import device as site_device

from ..exceptions import SyncError

MessageTuple = namedtuple('Message', 'index, total, inserted updated deleted producer tx_name tx_pk success')


class IncomingTransactionManager(models.Manager):

    def replace_pk_in_tx(self, old_pk, new_pk, using):
        """Replaces a pk for all unconsumed transactions."""
        incoming_transactions = super(IncomingTransactionManager, self).using(using).filter(
            is_consumed=False).order_by('timestamp')
        for incoming_transaction in incoming_transactions:
            field_cryptor = FieldCryptor('aes', 'local')
            tx = field_cryptor.decrypt(incoming_transaction.tx)
            if old_pk in tx:
                tx = tx.replace(old_pk, new_pk)
                incoming_transaction.tx = field_cryptor.encrypt(tx)
                incoming_transaction.save_base(using=using)

    def deserialize(self, model_name=None, producer_name=None, check_hostname=None,
                    ignore_device_id=None, custom_device=None):
        """Deserialize new incoming transactions."""
        device = custom_device or site_device
        check_hostname = True if check_hostname is None else check_hostname
        if not device.is_server:
            if not ignore_device_id:
                raise SyncError('Transactions can only be deserialized on a host that is server. '
                                'Got device id {}'.format(device.device_id))
        options = {'is_consumed': False, 'is_ignored': False}
        if model_name:
            options.update({'tx_name': self.model_name})
        if producer_name:
            options.update({'producer': self.producer_name})
        incoming_transactions = self.filter(**options).order_by('timestamp', 'producer')
        total = incoming_transactions.count()
        messages = []
        for index, incoming_transaction in enumerate(incoming_transactions):
            print(incoming_transaction.tx_name)
            inserted, updated, deleted = incoming_transaction.deserialize_transaction(check_hostname=check_hostname)
            messages.append(MessageTuple(
                index, total, inserted, updated, deleted,
                incoming_transaction.producer,
                incoming_transaction.tx_name,
                incoming_transaction.tx_pk,
                True))
        return messages

    def deserialized_message(self):
        today = timezone.now()
        margin = timedelta(days=1)
        deserialized_today = self.filter(
            created__range=(today - margin, today + margin), is_consumed=True)
        not_deserialized_today = self.filter(
            created__range=(today - margin, today + margin), is_consumed=False)
        not_deserialized_not_ignored_today = not_deserialized_today.filter(is_ignored=True)
        message = (
            '\'{0}\' transactions where received today, \n \'{1}\' transactions failed to save,\n'
            '\'{2}\' transactions that failed to save are set to be ignored.').format(
                deserialized_today.count(),
                not_deserialized_today.count(),
                not_deserialized_not_ignored_today.count())
        return message
