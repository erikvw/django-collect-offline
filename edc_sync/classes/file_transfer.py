import paramiko
import getpass
import os.path
from unipath import Path
from edc_sync.models import History
from datetime import datetime
from django.conf import settings
from django.apps import apps as django_apps
from edc_sync.constants import REMOTE, LOCALHOST


class FileConnector(object):

    def __init__(self, localhost, remote_device_sftp, is_archived=None, copy=None, source_folder=None,
                 destination_folder=None, archive_dir=None, filename=None, device=None):
        self.is_archived = True if is_archived else False
        self._copy = True if copy else False
        self.source_folder = source_folder
        self.destination_folder = destination_folder
        self.archive_dir = archive_dir
        self.filename = filename
        self.localhost = localhost
        self.remote_device_sftp = remote_device_sftp
        self.device = device or REMOTE

    def copy(self):
        """ Copy the file to remote device otherwise copies it to a local folder """
        local_filename = os.path.join(self.source_folder, self.filename)
        if self.device == REMOTE:
            remote_file_name = os.path.join(self.destination_folder, self.filename)
            sftp_attr = self.remote_device_sftp.put(local_filename, remote_file_name, confirm=True)
            return sftp_attr
        else:
            self.localhost_sftp.exec_command(
                "cd {} ; cp {} {}".format(self.source_folder, local_filename, self.destination_folder))
            return sftp_attr

    def move(self):
        """ Move the file to remote device otherwise it moves local folder. """
        local_filename = os.path.join(self.source_folder, self.filename)
        if self.device == REMOTE:
            remote_file_name = os.path.join(self.destination_folder, self.filename)
            self.remote_device_sftp.put(local_filename, remote_file_name, confirm=True)
            if self.is_archived:
                self.archive()
            return True
        else:
            filename = os.path.join(self.source_folder, self.filename)
            self.localhost.exec_command(
                "cd {} ; mv {} {}".format(self.source_folder, filename, self.destination_folder))
            return True
        return False

    def archive(self):
        """ Move file from the current dir to new dir called archive """
        filename = os.path.join(self.source_folder, self.filename)
        stdin, stdout, stderr = self.localhost.exec_command(
            "cd {} ; mv {} {}".format(self.source_folder, filename, self.archive_dir))
        return (stdin, stdout, stderr)

    def create_history(self):
        history = History.objects.create(
            filename=self.filename,
            acknowledged=True,
            ack_datetime=datetime.today(),
        )
        return history


class FileTransfer(object):
    """
        The class is responsible for transfer of different files from localhost to remote device.
    """

    def __init__(self):
        self.transaction_files = self.edc_sync_app_config.transaction_files
        self.transaction_files_archive = self.edc_sync_app_config.transaction_files_archive
        self.file_server = self.edc_sync_app_config.file_server
        self.file_server_folder = self.edc_sync_app_config.file_server_folder
        self.remote_user = self.edc_sync_app_config.remote_user
        self.media_dir = self.edc_sync_app_config.media_folders[0]

    @property
    def edc_sync_app_config(self):
        return django_apps.get_app_config('edc_sync')

    def connect_to_device(self, device):
        device, username = (self.file_server, self.remote_user) if device == REMOTE else (LOCALHOST, getpass.getuser())
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(device, username=username, look_for_keys=True)
        except paramiko.SSHException:
            raise False
        return client

    def filenames(self, source_dir):
        """ Returns a list transaction files to transfer to the remote device """
        localhost = self.connect_to_device(LOCALHOST)
        localhost_sftp = localhost.open_sftp()
        filenames = localhost_sftp.listdir(source_dir)
        localhost_sftp.close()
        return filenames

    def transfer_transactions(self):
        """ Copies the transaction file from localhost to remote device """
        remote_device = self.connect_to_device(REMOTE)
        remote_device_sftp = remote_device.open_sftp()
        localhost = self.connect_to_device(LOCALHOST)
        for file_name in self.filenames(self.transaction_files):
            connector = FileConnector(
                remote_device_sftp=remote_device_sftp, localhost=localhost, is_archived=True,
                source_folder=self.transaction_files, destination_folder=self.file_server_folder,
                filename=file_name, device=REMOTE, archive_dir=self.transaction_files_archive
            )
            connector.move()
            connector.create_history()

    def user_media_files_to_transfer(self, media_dir):
        """Returns a list of media file to send to the server. """
        user_media_files_to_transfer = self.filenames(media_dir)
        try:
            user_media_files_to_transfer.remove('.DS_Store')
        except ValueError:
            pass
        media_to_transfer = []
        for filename in user_media_files_to_transfer:
            try:
                History.objects.get(filename=filename)
            except History.DoesNotExist:
                media_to_transfer.append(filename)
        return media_to_transfer

    @property
    def transfer_media_files(self):
        """ Copies the transaction file from localhost to remote device """
        remote_device = self.connect_to_device(REMOTE)
        remote_device_sftp = remote_device.open_sftp()
        localhost = self.connect_to_device(LOCALHOST)
        for media_dir in self.media_dir:
            for file_name in self.user_media_files_to_transfer(media_dir):
                connector = FileConnector(
                    remote_device_sftp=remote_device_sftp, localhost=localhost,
                    is_archived=False, source_folder=self.media_dir, destination_folder=self.file_server_folder,
                    filename=file_name, device=REMOTE
                )
                connector.copy()
                connector.create_history()

    def count_sent_media(self, initial_media_files):
        """ Count number of registered media files based on the initial files to send."""
        return History.objects.filter(filename__in=initial_media_files).count()
