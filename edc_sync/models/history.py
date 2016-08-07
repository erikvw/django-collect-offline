from django.conf import settings
from django.db import models
from django.utils import timezone
from edc_sync.choices import STATUS


class History(models.Model):

    location = models.CharField(
        max_length=100,
        default='gaborone')

    remote_path = models.CharField(
        max_length=200)

    archive_path = models.CharField(
        max_length=100,
        null=True)

    filename = models.CharField(
        max_length=100,
        unique=True)

    filesize = models.FloatField(default=0.0)

    filetimestamp = models.DateTimeField(default=timezone.now)

    status = models.CharField(
        max_length=15,
        choices=STATUS,
        default=STATUS[0][0])

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

    class Meta:
        app_label = 'edc_sync'
        ordering = ('-sent_datetime', )
        verbose_name = 'Sent History'
        verbose_name_plural = 'Sent History'
