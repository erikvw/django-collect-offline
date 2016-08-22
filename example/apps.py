from django.apps import AppConfig as DjangoAppConfig
from django_crypto_fields.apps import AppConfig as DjangoCryptoFieldsAppConfigParent
from edc_sync.constants import CLIENT
from edc_sync.apps import AppConfig as EdcSyncAppConfigParent
from edc_base.apps import AppConfig as EdcBaseAppConfigParent
from edc_device.apps import AppConfig as EdcDeviceAppConfigParent


class AppConfig(DjangoAppConfig):
    name = 'example'
    verbose_name = 'Example Project'
    institution = 'Botswana-Harvard AIDS Institute Partnership'


class EdcDeviceAppConfig(EdcDeviceAppConfigParent):
    device_id = '15'


class EdcBaseAppConfig(EdcBaseAppConfigParent):
    institution = 'Botswana-Harvard AIDS Institute Partnership'
    verbose_name = 'Example Project'


class EdcSyncAppConfig(EdcSyncAppConfigParent):
    verbose_name = EdcSyncAppConfigParent.verbose_name + ' ' + CLIENT.title()
    role = CLIENT


class DjangoCryptoFieldsAppConfig(DjangoCryptoFieldsAppConfigParent):
    model = ('example', 'crypt')
    crypt_model_using = 'default'
