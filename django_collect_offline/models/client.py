from edc_base.model_mixins import BaseUuidModel

from .model_mixins import HostModelMixin
from .managers import HostManager


class Client(HostModelMixin, BaseUuidModel):

    """A model to capture the attributes of hosts (clients) to be
    contacted by the server.
    """

    objects = HostManager()

    class Meta:
        ordering = ['hostname', 'port']
        unique_together = (('hostname', 'port'),)
