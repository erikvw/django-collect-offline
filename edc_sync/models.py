import sys

from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models
from edc_base.model_mixins import BaseUuidModel
from edc_base.sites import CurrentSiteManager, SiteModelMixin
from edc_base.utils import get_utcnow

from .model_mixins import TransactionModelMixin, HostModelMixin


class IncomingTransaction(TransactionModelMixin, SiteModelMixin, BaseUuidModel):

    """ Transactions received from a remote host.
    """

    site = models.ForeignKey(
        Site, on_delete=models.CASCADE, null=True, editable=False)

    is_consumed = models.BooleanField(
        default=False)

    is_self = models.BooleanField(
        default=False)

    on_site = CurrentSiteManager()

    objects = models.Manager()

    class Meta:
        ordering = ['timestamp']


class OutgoingTransaction(TransactionModelMixin, SiteModelMixin, BaseUuidModel):

    """ Transactions produced locally to be consumed/sent
    to a queue or consumer.
    """

    site = models.ForeignKey(
        Site, on_delete=models.CASCADE, null=True, editable=False)

    is_consumed_middleman = models.BooleanField(
        default=False)

    is_consumed_server = models.BooleanField(
        default=False)

    using = models.CharField(max_length=25, null=True)

    on_site = CurrentSiteManager()

    objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.using:
            raise ValueError(
                'Value for \'{}.using\' cannot be None.'.format(
                    self._meta.model_name))
        if self.is_consumed_server and not self.consumed_datetime:
            self.consumed_datetime = get_utcnow()
        super().save(*args, **kwargs)

    class Meta:
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
        ordering = ['hostname', 'port']
        unique_together = (('hostname', 'port'),)


class Server(HostModelMixin, BaseUuidModel):

    """A model to capture the attributes of the server.
    """

    objects = HostManager()

    class Meta:
        ordering = ['hostname', 'port']
        unique_together = (('hostname', 'port'),)


class HistoryManager(models.Manager):

    def get_by_natural_key(self, filename, sent_datetime):
        return self.get(filename=filename, sent_datetime=sent_datetime)


# FIXME: is this model used?
class History(BaseUuidModel):

    objects = HistoryManager()

    filename = models.CharField(
        max_length=100,
        unique=True)

    hostname = models.CharField(
        max_length=100)

    sent_datetime = models.DateTimeField(default=get_utcnow)

    def __str__(self):
        return '</{}.{}>'.format(self.filename, self.hostname)

    def natural_key(self):
        return (self.filename, self.hostname)

    class Meta:
        ordering = ('-sent_datetime',)
        verbose_name = 'Sent History'
        verbose_name_plural = 'Sent History'
        unique_together = (('filename', 'hostname'),)


if 'edc_sync' in settings.APP_NAME and 'makemigrations' not in sys.argv:
    from .tests import models
