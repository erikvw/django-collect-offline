from django.db import models

from django_crypto_fields.fields import EncryptedCharField
from edc_base.model.models import BaseUuidModel


class Producer(BaseUuidModel):

    name = models.CharField(
        max_length=25,
        help_text='Usually hostname-database_name. e.g mpp83-bhp041_survey',
        unique=True)

    settings_key = models.CharField(
        max_length=25,
        help_text='Key in settings.DATABASES, usually hostname of producer',
        unique=True)

    url = models.CharField(max_length=64)

    db_host = models.CharField(
        verbose_name="Producer hostname.",
        max_length=25,
        null=True,
        help_text=("provide the hostname of the producer."))

    db_user = models.CharField(
        verbose_name="Database username.",
        max_length=25,
        default='root',
        null=True,
        help_text=("provide the database name of the producer."))

    db_name = models.CharField(
        verbose_name="Database name.",
        max_length=25,
        null=True,
        db_index=True,
        help_text=("provide the database name of the producer."))

    db_port = models.CharField(
        verbose_name="Database port.",
        max_length=25,
        default='',
        blank=True,
        null=True,
        help_text=("provide the database port of the producer."))

    db_password = EncryptedCharField(
        verbose_name="Database password.",
        max_length=50,
        help_text=("provide the password to database on the producer."))

    is_active = models.BooleanField(
        default=True)

    sync_datetime = models.DateTimeField(
        null=True)

    sync_status = models.CharField(
        max_length=250,
        default='-',
        null=True)

    json_limit = models.IntegerField(
        default=0)

    json_total_count = models.IntegerField(
        default=0)

    comment = models.TextField(
        max_length=50,
        null=True,
        blank=True)

    objects = models.Manager()

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'edc_sync'
        ordering = ['name']
        unique_together = (('settings_key', 'is_active'), )
