import sys

from django.apps import AppConfig as DjangoAppConfig
from django.apps import apps as django_apps
from django.core.management.color import color_style

style = color_style()


class AppConfig(DjangoAppConfig):
    name = 'edc_sync'
    verbose_name = 'Data Synchronization'
    edc_sync_files_using = False

    def ready(self):
        from .signals import create_auth_token, serialize_on_post_delete, serialize_m2m_on_save, serialize_on_save
        sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
        if not self.role:
            sys.stdout.write(style.NOTICE(
                ' Warning: Project uses \'edc_sync\' but has not defined a role for this '
                'app instance. See AppConfig.\n'))
        sys.stdout.write('  * device is a {} with ID {}\n'.format(self.role.lower(), self.device_id))
        sys.stdout.write(' Done loading {}.\n'.format(self.verbose_name))

    @property
    def role(self):
        """Return the role of this device.

        Role is configured through edc_device. Se edc_device.apps.AppConfig."""
        return django_apps.get_app_config('edc_device').role

    @property
    def device_id(self):
        """Return the ID of this device.

        Device ID is configured through edc_device. Se edc_device.apps.AppConfig."""
        return django_apps.get_app_config('edc_device').device_id
