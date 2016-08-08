import os
import getpass
import sys
from django.conf import settings

from django.apps import AppConfig as DjangoAppConfig
from django.core.management.color import color_style


class EdcSyncAppConfig(DjangoAppConfig):
    name = 'edc_sync'
    verbose_name = 'Data Synchronization'
    role = 'server'
    # make relative

    transaction_files = None
    transaction_files_archive = None

    media_folders = []

    file_server = None
    file_server_folder = None
    remote_username = None

    def ready(self):
        if not self.role:
            style = color_style()
            sys.stdout.write(style.NOTICE(
                'Warning: Project uses \'edc_sync\' but has not defined a role for this app instance. See AppConfig.\n'))
        self.transaction_files = os.path.join(settings.BASE_DIR, 'transactions')
        self.transaction_files_archive = os.path.join(settings.BASE_DIR, 'transactions', 'archive')
