from django.db import models

from edc.base.model.models import BaseUuidModel


class Consumer(BaseUuidModel):

    name = models.CharField(
        max_length=25,
        )

    ipaddress = models.CharField(
        max_length=64,
        )

    is_active = models.BooleanField(
        default=True
        )

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'sync'
        db_table = 'bhp_sync_consumer'
        ordering = ['name']
