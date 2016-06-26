import sys

from Crypto.Cipher import AES as AES_CIPHER

from django.apps import apps as django_apps
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django_crypto_fields.constants import LOCAL_MODE, AES, HASH_PREFIX
from django_crypto_fields.cryptor import Cryptor

from edc_sync.models import OutgoingTransaction, IncomingTransaction
from django_crypto_fields.field_cryptor import FieldCryptor


class Command(BaseCommand):

    def __init__(self, *args, **kwargs):
        self.aes_decrypt = Cryptor(aes_encryption_mode=AES_CIPHER.MODE_CFB).aes_decrypt
        self.aes_encrypt = Cryptor(aes_encryption_mode=AES_CIPHER.MODE_CBC).aes_encrypt
        self.decrypt_field = FieldCryptor(AES, LOCAL_MODE, aes_encryption_mode=AES_CIPHER.MODE_CFB).decrypt
        super(Command, self).__init__(*args, **kwargs)

    def handle(self, *args, **options):
        self.dry_run = True
        if self.dry_run:
            sys.stdout.write(self.style.NOTICE('\nDry run. No changes will be made.\n'))
        error_msg = (
            'Default encryption mode must be explicitly '
            'set to AES.MODE_CFB in settings. '
            '(settings.AES_ENCRYPTION_MODE=AES.MODE_CFB).')
        try:
            if settings.AES_ENCRYPTION_MODE != AES_CIPHER.MODE_CFB:
                raise CommandError('{} Got \'{}\''.format(error_msg, settings.AES_ENCRYPTION_MODE))
        except AttributeError:
            raise CommandError(error_msg)
        self.update_transactions()
        self.stdout.write('Done.\n')
        self.stdout.write(self.style.NOTICE(
            'Important! DO NOT FORGET to remove attribute AES_ENCRYPTION_MODE from settings.py NOW.\n'))

    def update_transactions(self):
        for i, transactions in enumerate(self.transactions()):
            total = transactions.count()
            sys.stdout.write('{}. {}: {}\n'.format(i + 2, transactions.model._meta.verbose_name, total))
            updated = 0
            skipped = 0
            for index, obj in enumerate(transactions):
                if obj.tx[0:len(HASH_PREFIX)] == HASH_PREFIX.encode():
                    obj.tx = self.cryptor.aes_encrypt(self.decrypt_field(obj.tx), mode=LOCAL_MODE)
                    if not self.dry_run:
                        obj.save()
                    updated += 1
                else:
                    skipped += 1
                sys.stdout.write('  ' + self.msg(total, index + 1, updated, skipped))
            self.stdout.write('\n')

    def transactions(self):
        for model in [OutgoingTransaction, IncomingTransaction]:
            yield model.objects.all().order_by('-timestamp')

    def msg(self, total, index, updated, skipped):
        return '{}/{}. Updated: {}  Skipped : {}\r'.format(index, total, updated, skipped)
