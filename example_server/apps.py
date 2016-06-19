from django.apps import AppConfig
from django_crypto_fields.apps import DjangoCryptoFieldsAppConfig
from edc_sync.constants import SERVER
from edc_sync.apps import EdcSyncAppConfig


class SyncAppConfig(EdcSyncAppConfig):
    name = 'edc_sync'
    verbose_name = EdcSyncAppConfig.verbose_name + ' ' + SERVER.title()
    role = SERVER


class ExampleAppConfig(AppConfig):
    name = 'example_server'
    verbose_name = 'Example Project'
    institution = 'Botswana-Harvard AIDS Institute Partnership'


class DjangoCryptoFieldsApp(DjangoCryptoFieldsAppConfig):
    name = 'django_crypto_fields'
    model = ('example', 'crypt')
    crypt_model_using = 'default'
