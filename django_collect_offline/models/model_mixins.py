from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe
from django_crypto_fields.constants import LOCAL_MODE
from django_crypto_fields.cryptor import Cryptor

from ..choices import ACTIONS


class TransactionModelMixin(models.Model):

    """Abstract model class for Incoming and Outgoing transactions.
    """

    tx = models.BinaryField()

    tx_name = models.CharField(
        max_length=64)

    tx_pk = models.UUIDField(
        db_index=True)

    producer = models.CharField(
        max_length=200,
        db_index=True,
        help_text='Producer name')

    action = models.CharField(
        max_length=1,
        choices=ACTIONS)

    timestamp = models.CharField(
        max_length=50,
        db_index=True)

    consumed_datetime = models.DateTimeField(
        null=True,
        blank=True)

    consumer = models.CharField(
        max_length=200,
        null=True,
        blank=True)

    is_ignored = models.BooleanField(
        default=False,
    )

    is_error = models.BooleanField(
        default=False)

    error = models.TextField(
        max_length=1000,
        null=True,
        blank=True)

    prev_batch_id = models.CharField(
        max_length=100,
        null=True,
        blank=True)

    batch_id = models.CharField(
        max_length=100,
        null=True,
        blank=True)

    def __str__(self):
        return f'{self._meta.model_name}.{self.tx_name}.{self.id}.{self.action}'

    def aes_decrypt(self, cipher):
        cryptor = Cryptor()
        plaintext = cryptor.aes_decrypt(cipher, LOCAL_MODE)
        return plaintext

    def aes_encrypt(self, plaintext):
        cryptor = Cryptor()
        cipher = cryptor.aes_encrypt(plaintext, LOCAL_MODE)
        return cipher

    def view(self):
        url = reverse('django_collect_offline:render_url',
                      kwargs={
                          'model_name': self._meta.object_name.lower(),
                          'pk': str(self.pk)})
        ret = mark_safe(
            '<a href="{url}" class="add-another" id="add_id_report" '
            'onclick="return showAddAnotherPopup(this);"> '
            '<img src="/static/admin/img/icon_addlink.gif" '
            'width="10" height="10" alt="View"/></a>'.format(url=url))
        return ret
    view.allow_tags = True

    class Meta:
        abstract = True


class HostModelMixin(models.Model):

    """Abstract class for hosts (either client or server).
    """

    hostname = models.CharField(
        max_length=200,
        unique=True)

    port = models.IntegerField(
        default='80')

    api_name = models.CharField(
        max_length=15,
        default='v1')

    format = models.CharField(
        max_length=15,
        default='json')

    authentication = models.CharField(
        max_length=15,
        default='api_key')

    is_active = models.BooleanField(
        default=True)

    last_sync_datetime = models.DateTimeField(
        null=True,
        blank=True)

    last_sync_status = models.CharField(
        max_length=250,
        default='-',
        null=True,
        blank=True)

    comment = models.TextField(
        max_length=50,
        null=True,
        blank=True)

    def __str__(self):
        return f'{self.hostname}:{self.port}'

    def natural_key(self):
        return (self.hostname, self.port, )

    @property
    def url_template(self):
        return (
            f'http://{self.hostname}:{self.port}/django_collect_offline/'
            f'api/{self.api_name}/')

    @property
    def url(self):
        return self.url_template.format(
            hostname=self.hostname, port=self.port, api_name=self.api_name)

    class Meta:
        abstract = True
