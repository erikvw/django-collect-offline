from django.apps import AppConfig
from django_crypto_fields.apps import DjangoCryptoFieldsAppConfig


class ExampleAppConfig(AppConfig):
    name = 'example'
    verbose_name = 'Example Project'
    institution = 'Botswana-Harvard AIDS Institute Partnership'


class DjangoCryptoFieldsApp(DjangoCryptoFieldsAppConfig):
    name = 'django_crypto_fields'
    model = ('example', 'crypt')
    crypt_model_using = 'default'
