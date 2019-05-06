from django.db import models
from django_crypto_fields.constants import LOCAL_MODE
from django_crypto_fields.cryptor import Cryptor

from ..choices import ACTIONS


class TransactionModelMixin(models.Model):

    """Abstract model class for Incoming and Outgoing transactions.
    """

    tx = models.BinaryField()

    tx_name = models.CharField(max_length=64)

    tx_pk = models.UUIDField(db_index=True)

    producer = models.CharField(
        max_length=200, db_index=True, help_text="Producer name"
    )

    action = models.CharField(max_length=1, choices=ACTIONS)

    timestamp = models.CharField(max_length=50, db_index=True)

    consumed_datetime = models.DateTimeField(null=True, blank=True)

    consumer = models.CharField(max_length=200, null=True, blank=True)

    is_ignored = models.BooleanField(default=False)

    is_error = models.BooleanField(default=False)

    error = models.TextField(max_length=1000, null=True, blank=True)

    prev_batch_id = models.CharField(max_length=100, null=True, blank=True)

    batch_id = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self._meta.model_name}.{self.tx_name}.{self.id}.{self.action}"

    def aes_decrypt(self, cipher):
        cryptor = Cryptor()
        plaintext = cryptor.aes_decrypt(cipher, LOCAL_MODE)
        return plaintext

    def aes_encrypt(self, plaintext):
        cryptor = Cryptor()
        cipher = cryptor.aes_encrypt(plaintext, LOCAL_MODE)
        return cipher

    @property
    def verbose_name(self):
        return self._meta.verbose_name

    class Meta:
        abstract = True
