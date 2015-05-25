from django.db import models
from django.utils import timezone

from edc_base.model.models import BaseUuidModel

from ..mixins import SyncMixin


class TestSync (BaseUuidModel, SyncMixin):

    character = models.CharField(
        max_length=10)

    integer = models.IntegerField()

    report_datetime = models.DateTimeField(
        default=timezone.now)

    report_date = models.DateField(
        default=timezone.now)

    objects = models.Manager()

    class Meta:
        app_label = 'edc_sync'
