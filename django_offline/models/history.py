from django.db import models
from edc_base.model_mixins import BaseUuidModel
from edc_base.utils import get_utcnow

from .managers import HistoryManager


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
        return f'</{self.filename}.{self.hostname}>'

    def natural_key(self):
        return (self.filename, self.hostname)

    class Meta:
        ordering = ('-sent_datetime',)
        verbose_name = 'Sent History'
        verbose_name_plural = 'Sent History'
        unique_together = (('filename', 'hostname'),)
