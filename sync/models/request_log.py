from datetime import datetime
from django.db import models
from edc.base.model.models import BaseUuidModel
from .producer import Producer


class RequestLog(BaseUuidModel):

    producer = models.ForeignKey(Producer)

    request_datetime = models.DateTimeField(
        default=datetime.today())

    status = models.CharField(
        max_length=25,
        default='complete')

    comment = models.CharField(
        max_length=100,
        null=True,
        blank=True)

    class Meta:
        app_label = 'sync'
        db_table = 'bhp_sync_requestlog'
