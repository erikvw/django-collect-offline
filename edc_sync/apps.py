import sys
import os

from django.apps import AppConfig as DjangoAppConfig
from django.apps import apps as django_apps
from django.conf import settings
from django.core.management.color import color_style

from .site_sync_models import site_sync_models

from edc_sync.constants import CLIENT
from edc_sync_files.apps import AppConfig as BaseEdcSyncFilesAppConfig

style = color_style()


class SyncConfigError(Exception):
    pass


class AppConfig(DjangoAppConfig):
    name = 'edc_sync'
    verbose_name = 'Data Synchronization'
    edc_sync_files_using = False
    base_template_name = 'edc_base/base.html'
    server_ip = None
    role = None

    def ready(self):
        from .signals import create_auth_token, serialize_on_post_delete, serialize_m2m_on_save, serialize_on_save
        sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
        if not self.role:
            sys.stdout.write(style.NOTICE(
                ' Warning: Project uses \'edc_sync\' but has not defined a role for this '
                'app instance. See AppConfig.\n'))
#         sys.stdout.write(
#             '  * device is a {} with ID {}\n'.format(self.role.lower()))
        site_sync_models.autodiscover()
        sys.stdout.write(' Done loading {}.\n'.format(self.verbose_name))

#     @property
#     def role(self):
#         """Return the role of this device.
#
#         Role is configured through edc_device. Se edc_device.apps.AppConfig."""
#         return django_apps.get_app_config('edc_device').role

    @property
    def server(self):
        if self.role == CLIENT:
            if not self.server_ip:
                raise SyncConfigError(
                    'Provide server ip address, it is required '
                    'for synchronization.')
            else:
                return self.server_ip

    @property
    def device_id(self):
        """Return the ID of this device.

        Device ID is configured through edc_device. Se edc_device.apps.AppConfig."""
        return django_apps.get_app_config('edc_device').device_id


class EdcSyncFilesAppConfig(BaseEdcSyncFilesAppConfig):
    edc_sync_files_using = True
    config_subfolder_name = 'bcpp'
    role = CLIENT
    #
    user = 'django'
    host = '192.168.1.85'
    password = None
    source_folder = os.path.join(
        settings.MEDIA_ROOT, 'transactions', 'outgoing')
    destination_folder = os.path.join(
        settings.MEDIA_ROOT, 'transactions', 'incoming')
    archive_folder = os.path.join(
        settings.MEDIA_ROOT, 'transactions', 'archive')
