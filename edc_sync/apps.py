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
    config_filename = 'edc_sync.ini'
#     default_config = {
#         'user': 'django',
#         'file_server': 'localhost',
#         'file_server_folder': '~/edc_sync_files'}
    transaction_files = None
    transaction_files_archive = None

    media_folders = []

    file_server = None
    file_server_folder = None
    remote_username = None

    def ready(self):
        sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
        if not self.role:
            sys.stdout.write(style.NOTICE(
                'Warning: Project uses \'edc_sync\' but has not defined a role for this app instance. '
                'See AppConfig.\n'))
        self.transaction_files = os.path.join(settings.BASE_DIR, 'transactions')
        self.transaction_files_archive = os.path.join(settings.BASE_DIR, 'transactions', 'archive')
        self.set_config_attrs()
        sys.stdout.write(' Done loading {}.\n'.format(self.verbose_name))
