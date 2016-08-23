import sys

from django.apps import AppConfig as DjangoAppConfig
from django.core.management.color import color_style

from django_appconfig_ini.mixin import ConfigIniMixin

style = color_style()


class AppConfig(ConfigIniMixin, DjangoAppConfig):
    name = 'edc_sync'
    verbose_name = 'Data Synchronization'
    role = 'server'
    config_ini_attrs = {'edc_sync': ['role']}

    def ready(self):
        sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
        self.overwrite_config_ini_attrs_on_class(self.name)
        if not self.role:
            sys.stdout.write(style.NOTICE(
                ' Warning: Project uses \'edc_sync\' but has not defined a role for this '
                'app instance. See AppConfig.\n'))
        sys.stdout.write(' * role is {}.\n'.format(self.role.upper()))
        sys.stdout.write(' Done loading {}.\n'.format(self.verbose_name))
