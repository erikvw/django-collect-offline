from django.db import models
from edc.core.crypto_fields.classes import FieldCryptor


class IncomingTransactionManager(models.Manager):

    def replace_pk_in_tx(self, old_pk, new_pk, using):
        """Replaces a pk for all unconsumed transactions."""
        for incoming_transaction in super(IncomingTransactionManager, self).using(using).filter(is_consumed=False).order_by('timestamp'):
            field_cryptor = FieldCryptor('aes', 'local')
            tx = field_cryptor.decrypt(incoming_transaction.tx)
            if old_pk in tx:
                tx = tx.replace(old_pk, new_pk)
                incoming_transaction.tx = field_cryptor.encrypt(tx)
                incoming_transaction.save_base(using=using)
