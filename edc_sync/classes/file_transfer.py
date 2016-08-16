import paramiko
import getpass
import os.path
from edc_sync.models import History
from datetime import datetime
from django.apps import apps as django_apps
from edc_sync.constants import REMOTE, LOCALHOST


class FileConnector(object):

    def __init__(self, localhost=None, remote_device_sftp=None, is_archived=None, copy=None, source_folder=None,
                 destination_folder=None, archive_dir=None, filename=None, pull=None, hostname=None):
        self.is_archived = True if is_archived else False
        self._copy = True if copy else False
        self.source_folder = source_folder
        self.destination_folder = destination_folder
        self.archive_dir = archive_dir
        self.filename = filename
        self.localhost = localhost
        self.remote_device_sftp = remote_device_sftp
        self.pull = pull or False
        self.hostname = hostname

    def copy(self):
        """ Copy the file to remote device otherwise copies it to a local folder. Push (put) or Pull (get)."""
        if self.pull:
            local_filename = os.path.join(self.destination_folder, self.filename)
            remote_file_name = os.path.join(self.source_folder, self.filename)
            sftp_attr = self.remote_device_sftp.get(remote_file_name, local_filename)
            self.create_history()
        else:
            local_filename = os.path.join(self.source_folder, self.filename)
            remote_file_name = os.path.join(self.destination_folder, self.filename)
            sftp_attr = self.remote_device_sftp.put(remote_file_name, local_filename, confirm=True)
            return sftp_attr

    def move(self):
        """ Copies the files to remote device and move them to archive dir. """
        local_filename = os.path.join(self.source_folder, self.filename)
        if not self.pull:
            remote_file_name = os.path.join(self.source_folder, self.filename)
            self.remote_device_sftp.put(local_filename, remote_file_name, confirm=True)
            if self.is_archived:
                self.archive()
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
            hostname=self.hostname
        )
        return history


class FileTransfer(object):
    """
        The class is responsible for transfer of different files from localhost to remote device.
    """

    def __init__(self, file_server=None, media_dir=None, filename=None, file_server_folder=None, media_dir_upload=None, hostname=None):
        self.filename = filename
        self.file_server = file_server or self.edc_sync_app_config.file_server
        self.file_server_folder = file_server_folder or self.edc_sync_app_config.file_server_folder
        self.remote_user = self.edc_sync_app_config.user
        self.media_dir = media_dir or self.edc_sync_app_config.media_folders
        self.media_dir_upload = media_dir_upload or self.edc_sync_app_config.media_dir_upload
        self.hostname = hostname or self.remote_device_hostname

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
            return False
        return client

    @property
    def remote_device_hostname(self):
        remote_device = self.connect_to_device(REMOTE)
        _, stdout, _ = remote_device.exec_command('hostname')
        hostname = stdout.read()
        if isinstance(hostname, bytes):
            hostname = hostname.decode('utf-8')
        remote_device.close()
        print("remote_device.exec_command('hostname')", str(hostname))
        return hostname

    @property
    def media_filenames_remote_device(self):
        remote_device = self.connect_to_device(REMOTE)
        remote_device_sftp = remote_device.open_sftp()
        filenames = remote_device_sftp.listdir(self.file_server_folder)
        try:
            filenames.remove('.DS_Store')
        except ValueError:
            pass
        remote_device.close()
        remote_device_sftp.close()
        return filenames

    def media_files_to_copy(self):
        media_file_to_copy = []
        for filename in self.media_filenames_remote_device:
            try:
                History.objects.get(filename=filename, hostname=self.hostname)
            except History.DoesNotExist:
                media_file_to_copy.append(filename)
        return media_file_to_copy

    @property
    def media_filenames(self):
        localhost = self.connect_to_device(LOCALHOST)
        localhost_sftp = localhost.open_sftp()
        media_files = []
        for media_dir in self.media_dir:
            filenames = localhost_sftp.listdir(media_dir)
            try:
                filenames.remove('.DS_Store')
            except ValueError:
                pass
            media_files.append((media_dir, filenames))
        return media_files

    def pending_media_files(self):
        pending_media_files = []
        for media_dir, filenames in self.media_filenames:
            required_filenames = []
            for filename in filenames:
                try:
                    History.objects.get(filename=filename)
                except History.DoesNotExist:
                    required_filenames.append(filename)
            pending_media_files.append(dict({'media_dir': media_dir, "required_files": required_filenames}))
        return pending_media_files

    def pull_media_files(self):
        """ Copies the files from the remote machine into local machine """
        try:
            remote_device = self.connect_to_device(REMOTE)
            remote_device_sftp = remote_device.open_sftp()
            connector = FileConnector(
                remote_device_sftp=remote_device_sftp, pull=True, filename=self.filename, is_archived=False,
                source_folder=self.file_server_folder, destination_folder=self.media_dir_upload,
                hostname=self.hostname
            )
            connector.copy()
            remote_device.close()
            remote_device_sftp.close()
        except paramiko.SSHException:
            return False
        return True
