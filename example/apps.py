from django.apps import AppConfig
from django_crypto_fields.apps import DjangoCryptoFieldsAppConfig
from edc_sync.constants import CLIENT
from edc_sync.apps import EdcSyncAppConfig


class SyncAppConfig(EdcSyncAppConfig):
    name = 'edc_sync'
    verbose_name = EdcSyncAppConfig.verbose_name + ' ' + CLIENT.title()
    role = CLIENT


class ExampleAppConfig(AppConfig):
    name = 'example'
    verbose_name = 'Example Project'
    institution = 'Botswana-Harvard AIDS Institute Partnership'


class DjangoCryptoFieldsApp(DjangoCryptoFieldsAppConfig):
    name = 'django_crypto_fields'
    model = ('example', 'crypt')
    crypt_model_using = 'default'
