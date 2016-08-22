import os
import sys

from django.apps import AppConfig as DjangoAppConfig
from django.conf import settings
from django.core.management.color import color_style

from edc_base.config_parser_mixin import ConfigParserMixin

style = color_style()


class AppConfig(ConfigParserMixin, DjangoAppConfig):
    name = 'edc_sync'
    verbose_name = 'Data Synchronization'
    role = 'server'

    def ready(self):
        sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
        if not self.role:
            sys.stdout.write(style.NOTICE(
                ' Warning: Project uses \'edc_sync\' but has not defined a role for this '
                'app instance. See AppConfig.\n'))
        sys.stdout.write(' * role is {}.\n'.format(self.role.upper()))
        sys.stdout.write(' Done loading {}.\n'.format(self.verbose_name))
