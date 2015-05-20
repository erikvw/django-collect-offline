from datetime import datetime, date

from django.db import models

from ..mixins import SyncMixin


class TestModel (models.Model, SyncMixin):

    character = models.CharField(
        max_length=10)

    integer = models.IntegerField()

    report_datetime = models.DateField(
        default=datetime.today())

    report_date = models.DateField(
        default=date.today())

    objects = models.Manager()

    class Meta:
        app_label = 'edc_sync'
