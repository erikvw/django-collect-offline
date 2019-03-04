from django.db import models
from edc_model.models import BaseUuidModel

from ..model_mixins import HostModelMixin


class ClientManager(models.Manager):
    def get_by_natural_key(self, hostname):
        return self.get(hostname=hostname)


class Client(HostModelMixin, BaseUuidModel):

    """A model to capture the attributes of hosts (clients) to be
    contacted by the server.
    """

    objects = ClientManager()

    class Meta:
        ordering = ["hostname", "port"]
