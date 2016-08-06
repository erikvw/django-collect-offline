import getpass
import sys
from django.conf import settings

from django.apps import AppConfig as DjangoAppConfig
from django.core.management.color import color_style


class EdcSyncAppConfig(DjangoAppConfig):
    name = 'edc_sync'
    verbose_name = 'Data Synchronization'
    role = 'server'

    remote_server_ip = None
    remote_username = 'django'
    remote_dump_tx_files = '/Users/{}/transaction_json_files/dump'.format(remote_username)
    remote_user_media_files = '/Users/{}/transaction_json_files/media/to_upload'.format(remote_username)

    user_dump_tx_files = '/Users/{}/source/bcpp-interview/bcpp_interview/media/edc_sync/user_tx_files/dump'.format(getpass.getuser())
    user_archived_tx_files = '/Users/{}/source/bcpp-interview/bcpp_interview/media/edc_sync/user_tx_files/archived'.format(getpass.getuser())

    user_media_files = '/Users/{}/source/bcpp-interview/bcpp_interview/media/upload'.format(getpass.getuser())
    location = None

    def ready(self):
        if not self.role:
            style = color_style()
            sys.stdout.write(style.NOTICE(
                'Warning: Project uses \'edc_sync\' but has not defined a role for this app instance. See AppConfig.\n'))
        if settings.EDC_SYNC_REMOTE_FILE_SERVER:
            if not self.remote_server_ip or not self.remote_user_media_files:
                style = color_style()
                sys.stdout.write(style.NOTICE(
                    'Warning: Project uses \'edc_sync file transfer\' but has not defined a required attributes for this app instance. See AppConfig.\n'))
