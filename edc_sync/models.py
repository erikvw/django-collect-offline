import socket

from django.apps import apps as django_apps
from django.core import serializers
from django.core.urlresolvers import reverse
from django.db import models, transaction
from django.utils import timezone
from django_crypto_fields.constants import LOCAL_MODE
from django_crypto_fields.cryptor import Cryptor

from edc_base.model.models import BaseUuidModel

from .choices import ACTIONS
from .exceptions import SyncError

edc_device_app_config = django_apps.get_app_config('edc_device')


class BaseTransaction(BaseUuidModel):

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

    batch_seq = models.IntegerField(null=True, blank=True)

    batch_id = models.IntegerField(null=True, blank=True)

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self.tx_name)

    def __str__(self):
        return '</{}.{}/{}/{}/{}/>'.format(
            self._meta.app_label, self._meta.model_name, self.id, self.tx_name, self.action)

    def aes_decrypt(self, cipher):
        cryptor = Cryptor()
        plaintext = cryptor.aes_decrypt(cipher, LOCAL_MODE)
        return plaintext

    def aes_encrypt(self, plaintext):
        cryptor = Cryptor()
        cipher = cryptor.aes_encrypt(plaintext, LOCAL_MODE)
        return cipher

    def view(self):
        url = reverse('render_url',
                      kwargs={
                          'model_name': self._meta.object_name.lower(),
                          'pk': self.pk})
        ret = ('<a href="{url}" class="add-another" id="add_id_report" '
               'onclick="return showAddAnotherPopup(this);"> <img src="/static/admin/img/icon_addlink.gif" '
               'width="10" height="10" alt="View"/></a>'.format(url=url))
        return ret
    view.allow_tags = True

    class Meta:
        abstract = True


class IncomingTransaction(BaseTransaction):

    """ Transactions received from a remote host. """

    check_hostname = None

    is_consumed = models.BooleanField(
        default=False)

    is_self = models.BooleanField(
        default=False)

    def deserialize_transaction(self, check_hostname=None, commit=True, check_device=True):
        if check_device:
            if not edc_device_app_config.is_server:
                raise SyncError('Objects may only be deserialized on a server. Got device={} {}.'.format(
                    edc_device_app_config.device_id, edc_device_app_config.role))
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


class OutgoingTransaction(BaseTransaction):

    """ Transactions produced locally to be consumed/sent to a queue or consumer. """

    is_consumed_middleman = models.BooleanField(
        default=False)

    # not required, remove
    is_consumed_server = models.BooleanField(
        default=False)

    using = models.CharField(max_length=25, null=True)

    def save(self, *args, **kwargs):
        if not self.using:
            raise ValueError('Value for \'{}.using\' cannot be None.'.format(self._meta.model_name))
        if self.is_consumed_server and not self.consumed_datetime:
            self.consumed_datetime = timezone.now()
        super(OutgoingTransaction, self).save(*args, **kwargs)

    class Meta:
        app_label = 'edc_sync'
        ordering = ['timestamp']


class HostManager(models.Manager):

    def get_by_natural_key(self, hostname, port):
        return self.get(hostname=hostname, port=port)


class Host(BaseUuidModel):

    """Abstract class for hosts (either client or server)."""

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

    objects = HostManager()

    def __str__(self):
        return '{}:{}'.format(self.hostname, self.port)

    def natural_key(self):
        return (self.hostname, self.port, )

    @property
    def url_template(self):
        return 'http://{hostname}:{port}/edc-sync/api/{api_name}/'

    @property
    def url(self):
        return self.url_template.format(
            hostname=self.hostname, port=self.port, api_name=self.api_name)

    class Meta:
        abstract = True


class Client(Host):

    """A model to capture the attributes of hosts (clients) to be contacted by the server."""

    class Meta:
        app_label = 'edc_sync'
        ordering = ['hostname', 'port']
        unique_together = (('hostname', 'port'), )


class Server(Host):

    """A model to capture the attributes of the server."""

    class Meta:
        app_label = 'edc_sync'
        ordering = ['hostname', 'port']
        unique_together = (('hostname', 'port'), )


class HistoryManager(models.Manager):
    def get_by_natural_key(self, filename, sent_datetime):
        return self.get(filename=filename, sent_datetime=sent_datetime)


class History(BaseUuidModel):

    objects = HistoryManager()

    filename = models.CharField(
        max_length=100,
        unique=True)

    hostname = models.CharField(
        max_length=100
    )

    sent_datetime = models.DateTimeField(default=timezone.now)

    acknowledged = models.BooleanField(
        default=False,
        blank=True,
    )

    ack_datetime = models.DateTimeField(
        default=timezone.now,
        null=True,
        blank=True)

    ack_user = models.CharField(
        max_length=50,
        null=True,
        blank=True)

    def natural_key(self):
        return (self.filename, self.hostname)

    def __str__(self):
        return '</{}.{}>'.format(self.filename, self.hostname)

    class Meta:
        app_label = 'edc_sync'
        ordering = ('-sent_datetime', )
        verbose_name = 'Sent History'
        verbose_name_plural = 'Sent History'
        unique_together = (('filename', 'hostname'),)
