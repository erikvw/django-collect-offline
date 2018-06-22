from edc_base.model_mixins import BaseUuidModel

from .managers import HostManager
from .model_mixins import HostModelMixin


class Server(HostModelMixin, BaseUuidModel):

    """A model to capture the attributes of the server.
    """

    objects = HostManager()

    class Meta:
        ordering = ['hostname', 'port']
        unique_together = (('hostname', 'port'),)
