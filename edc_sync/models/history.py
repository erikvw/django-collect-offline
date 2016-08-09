from django.conf import settings
from django.db import models
from django.utils import timezone
from edc_sync.models.sync_model_mixin import SyncModelMixin
from edc_base.model.models import BaseUuidModel


class HistoryManager(models.Manager):
    def get_by_natural_key(self, filename, sent_datetime):
        return self.get(filename=filename, sent_datetime=sent_datetime)


class History(BaseUuidModel, SyncModelMixin):

    objects = HistoryManager()

    filename = models.CharField(
        max_length=100,
        unique=True)

    sent_datetime = models.DateTimeField(default=timezone.now)

    acknowledged = models.BooleanField(
        default=False,
        blank=True,
    )

    ack_datetime = models.DateTimeField(
        default=timezone.now,
        null=True,
        blank=True)

    ack_user = models.CharField(
        max_length=50,
        null=True,
        blank=True)

    def natural_key(self):
        return (self.filename, self.sent_datetime)

    class Meta:
        app_label = 'edc_sync'
        ordering = ('-sent_datetime', )
        verbose_name = 'Sent History'
        verbose_name_plural = 'Sent History'
        unique_together = (('filename', 'sent_datetime'),)
