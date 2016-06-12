from django.apps import AppConfig
from django_crypto_fields.apps import DjangoCryptoFieldsAppConfig


class EdcSyncAppConfig(AppConfig):
    name = 'edc_sync'
    verbose_name = 'Data Synchronization'


class DjangoCryptoFieldsApp(DjangoCryptoFieldsAppConfig):
    name = 'django_crypto_fields'
    model = ('example', 'crypt')
