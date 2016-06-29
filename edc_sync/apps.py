import sys

from django.apps import AppConfig
from django_crypto_fields.apps import DjangoCryptoFieldsAppConfig
from django.core.management.color import color_style


class EdcSyncAppConfig(AppConfig):
    name = 'edc_sync'
    verbose_name = 'Data Synchronization'
    role = None

    def ready(self):
        if not self.role:
            style = color_style()
            sys.stdout.write(style.NOTICE(
                'Warning: Project uses \'edc_sync\' but has not defined a role for this app instance. See AppConfig.\n'))


class DjangoCryptoFieldsApp(DjangoCryptoFieldsAppConfig):
    name = 'django_crypto_fields'
    model = ('example', 'crypt')
    crypt_model_using = 'default'
