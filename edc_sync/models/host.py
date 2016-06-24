from django.db import models

from edc_base.model.models import BaseUuidModel


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
