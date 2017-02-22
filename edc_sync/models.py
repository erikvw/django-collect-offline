import socket

from django.apps import apps as django_apps
from django.core import serializers
from django.db import models, transaction

from edc_base.model.models import BaseUuidModel
from edc_base.utils import get_utcnow

from .exceptions import SyncError
from .model_mixins import TransactionMixin, HostModelMixin

edc_device_app_config = django_apps.get_app_config('edc_device')


class IncomingTransaction(TransactionMixin, BaseUuidModel):

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
                raise SyncError(
                    'Incoming transactions exist that are from this host.')
            elif commit:
                if self.action == 'D':
                    deleted += self._deserialize_delete_tx(deserialized_object)
                elif self.action == 'I':
                    inserted += self._deserialize_insert_tx(
                        deserialized_object)
                elif self.action == 'U':
                    updated += self._deserialize_update_tx(deserialized_object)
                else:
                    raise SyncError(
                        'Unexpected value for action. Got {}'.format(self.action))
                if any([inserted, deleted, updated]):
                    self.is_ignored = False
                    self.is_consumed = True
                    self.consumed_datetime = get_utcnow()
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


class OutgoingTransaction(TransactionMixin, BaseUuidModel):

    """ Transactions produced locally to be consumed/sent to a queue or consumer. """

    is_consumed_middleman = models.BooleanField(
        default=False)

    # not required, remove
    is_consumed_server = models.BooleanField(
        default=False)

    using = models.CharField(max_length=25, null=True)

    def save(self, *args, **kwargs):
        if not self.using:
            raise ValueError(
                'Value for \'{}.using\' cannot be None.'.format(self._meta.model_name))
        if self.is_consumed_server and not self.consumed_datetime:
            self.consumed_datetime = get_utcnow()
        super(OutgoingTransaction, self).save(*args, **kwargs)

    class Meta:
        app_label = 'edc_sync'
        ordering = ['timestamp']


class HostManager(models.Manager):

    def get_by_natural_key(self, hostname, port):
        return self.get(hostname=hostname, port=port)


class Client(HostModelMixin, BaseUuidModel):

    """A model to capture the attributes of hosts (clients) to be contacted by the server."""

    objects = HostManager()

    class Meta:
        app_label = 'edc_sync'
        ordering = ['hostname', 'port']
        unique_together = (('hostname', 'port'), )


class Server(HostModelMixin, BaseUuidModel):

    """A model to capture the attributes of the server."""

    objects = HostManager()

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

    sent_datetime = models.DateTimeField(default=get_utcnow)

    acknowledged = models.BooleanField(
        default=False,
        blank=True,
    )

    ack_datetime = models.DateTimeField(
        default=get_utcnow,
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
