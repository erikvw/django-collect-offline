from django.db import models

from edc_base.encrypted_fields import EncryptedCharField
from edc_base.model.models import BaseUuidModel

from ..classes import PasswordModelField


class Producer(BaseUuidModel):

    name = models.CharField(
        max_length=50,
        help_text='Usually hostname-database_name. e.g mpp83-bhp041_survey',
        unique=True)

    settings_key = models.CharField(
        max_length=50,
        help_text='Key in settings.DATABASES, usually hostname of producer',
        unique=True)

    url = models.CharField(max_length=64)

    # TODO: change this in next revision! should be db_host
    producer_ip = EncryptedCharField(
        verbose_name="Producer IP address.",
        null=True,
        db_index=True,
        help_text=("provide the IP address of the producer."))

    db_user = EncryptedCharField(
        verbose_name="Database username.",
        default='root',
        null=True,
        db_index=True,
        help_text=("provide the database name of the producer."))

    # TODO: change this in next revision! should be db_name
    db_user_name = EncryptedCharField(
        verbose_name="Database name.",
        null=True,
        db_index=True,
        help_text=("provide the database name of the producer."))

    port = EncryptedCharField(
        verbose_name="Database port.",
        default='',
        blank=True,
        null=True,
        help_text=("provide the database name of the producer."))

    db_password = PasswordModelField(
        verbose_name="Database password.",
        max_length=250,
        null=True,
        db_index=True,
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

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'sync'
        db_table = 'bhp_sync_producer'
        ordering = ['name']
        unique_together = (('settings_key', 'is_active'), )
