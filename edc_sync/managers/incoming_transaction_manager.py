from django.db import models

from edc_base.encrypted_fields import FieldCryptor


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
