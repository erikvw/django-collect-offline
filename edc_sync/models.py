from django.apps import apps as django_apps
from django.db import models
from django.utils import timezone

from edc_base.model_mixins import BaseUuidModel
from edc_base.utils import get_utcnow

from .model_mixins import TransactionMixin, HostModelMixin

edc_device_app_config = django_apps.get_app_config('edc_device')


class IncomingTransaction(TransactionMixin, BaseUuidModel):

    """ Transactions received from a remote host.
    """

    is_consumed = models.BooleanField(
        default=False)

    is_self = models.BooleanField(
        default=False)

    class Meta:
        app_label = 'edc_sync'
        ordering = ['timestamp', 'producer']


class OutgoingTransaction(TransactionMixin, BaseUuidModel):

    """ Transactions produced locally to be consumed/sent to a queue or
        consumer.
    """

    is_consumed_middleman = models.BooleanField(
        default=False)

    is_consumed_server = models.BooleanField(
        default=False)

    using = models.CharField(max_length=25, null=True)

    def save(self, *args, **kwargs):
        if not self.using:
            raise ValueError(
                'Value for \'{}.using\' cannot be None.'.format(
                    self._meta.model_name))
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

    """A model to capture the attributes of hosts (clients) to be
    contacted by the server.
    """

    objects = HostManager()

    class Meta:
        app_label = 'edc_sync'
        ordering = ['hostname', 'port']
        unique_together = (('hostname', 'port'),)


class Server(HostModelMixin, BaseUuidModel):

    """A model to capture the attributes of the server.
    """

    objects = HostManager()

    class Meta:
        app_label = 'edc_sync'
        ordering = ['hostname', 'port']
        unique_together = (('hostname', 'port'),)


class SyncConfirmation(BaseUuidModel):

    code = models.CharField(
        max_length=200)

    confirm_code = models.CharField(
        max_length=200,
        null=True,
        blank=True)

    hostname = models.CharField(
        max_length=200)

    confirmed_by = models.CharField(
        max_length=100,
        blank=True,
        null=True)

    confirmed_date = models.DateField(
        default=timezone.now)

    sync_file = models.CharField(
        max_length=240)

    class Meta:
        app_label = 'edc_sync'
        ordering = ('-received_date',)
        unique_together = (('hostname', 'received_date'),)


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
        ordering = ('-sent_datetime',)
        verbose_name = 'Sent History'
        verbose_name_plural = 'Sent History'
        unique_together = (('filename', 'hostname'),)
