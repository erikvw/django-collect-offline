import sys

from django.apps import AppConfig as DjangoAppConfig
from django.core.management.color import color_style


class AppConfig(DjangoAppConfig):
    name = 'edc_sync'
    verbose_name = 'Data Synchronization'
    role = 'server'

    def ready(self):
        if not self.role:
            style = color_style()
            sys.stdout.write(style.NOTICE(
                'Warning: Project uses \'edc_sync\' but has not defined a role for this app instance. See AppConfig.\n'))
