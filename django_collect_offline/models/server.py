from django.db import models
from edc_model.models import BaseUuidModel

from ..model_mixins import HostModelMixin


class ServerManager(models.Manager):
    def get_by_natural_key(self, hostname):
        return self.get(hostname=hostname)


class Server(HostModelMixin, BaseUuidModel):

    """A model to capture the attributes of the server.
    """

    objects = ServerManager()

    class Meta:
        ordering = ["hostname", "port"]
