from django.apps import AppConfig as DjangoAppConfig
from django_crypto_fields.apps import AppConfig as DjangoCryptoFieldsAppConfigParent
from edc_sync.constants import SERVER
from edc_sync.apps import AppConfig as EdcSyncAppConfigParent
from edc_device.apps import AppConfig as EdcDeviceAppConfigParent


class AppConfig(DjangoAppConfig):
    name = 'example_server'
    verbose_name = 'Example Project'
    institution = 'Botswana-Harvard AIDS Institute Partnership'


class EdcSyncAppConfig(EdcSyncAppConfigParent):
    name = 'edc_sync'
    verbose_name = EdcSyncAppConfigParent.verbose_name + ' ' + SERVER.title()
    role = SERVER


class DjangoCryptoFieldsAppConfig(DjangoCryptoFieldsAppConfigParent):
    name = 'django_crypto_fields'
    model = ('example', 'crypt')
    crypt_model_using = 'default'


class EdcDeviceAppConfig(EdcDeviceAppConfigParent):
    device_id = '99'
