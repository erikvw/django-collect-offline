import logging
import paramiko
import getpass
from unipath import Path
from edc_sync.models import History
from datetime import datetime
from django.conf import settings
from django.core.management.color import color_style
from django.apps import apps as django_apps
logger = logging.getLogger(__name__)


class EdcSyncFileTransfer(object):

    def __init__(self, remote_server_ip=None, remote_dir=None, remote_username=None, remote_password=None,
                 user_tx_files=None, media_dir=None, remote_media_dir=None, tx_archive_dir=None,
                 client_password=None, archived_media_dir=None):

        self.remote_server_ip = self.edc_sync_app_config.remote_server_ip
        self.remote_user_media_files = self.edc_sync_app_config.remote_user_media_files
        self.remote_dump_tx_files = self.edc_sync_app_config.remote_dump_tx_files
        self.remote_username = self.edc_sync_app_config.remote_username

        self.user_dump_tx_files = user_tx_files or self.edc_sync_app_config.user_dump_tx_files
        self.user_archived_tx_files = user_tx_files or self.edc_sync_app_config.user_archived_tx_files
        self.user_media_files = self.edc_sync_app_config.user_media_files

        self.media_remote_dir = remote_media_dir
        self.archive_dir = None
        self.location = self.edc_sync_app_config.location

        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    @property
    def edc_sync_app_config(self):
        return django_apps.get_app_config('edc_sync')

    def connect_to_remote_server(self):
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(self.remote_server_ip, username=self.remote_username, look_for_keys=True)
            return (self.client, "connected to the server. {} - {}.".format(self.remote_server_ip, datetime.today()))
        except paramiko.SSHException as e:
            raise paramiko.SSHException("Failed to the server. {}. {}".format(self.remote_server_ip, e))

    def connect_localhost(self):
        try:
            self.client.connect('localhost', username=getpass.getuser(), look_for_keys=True)
            return (self.client, "connected to localhost. {}".format(datetime.today()))
        except paramiko.SSHException as e:
            raise paramiko.SSHException("{}".format(e))

    @property
    def user_tx_files(self):
        client, message = self.connect_localhost()
        self.log_message(message, "info")
        sftp = client.open_sftp()
        file_names = sftp.listdir(self.user_dump_tx_files)
        print("user_tx_files:", file_names)
        client.close()
        return file_names

    @property
    def user_media_files_to_transfer(self):
        client, message = self.connect_localhost()
        self.log_message(message, "info")
        sftp = client.open_sftp()
        filenames = sftp.listdir(self.user_media_files)
        try:
            filenames.remove('.DS_Store')
        except ValueError:
            pass
        media_to_transfer = []
        for filename in filenames:
            try:
                History.objects.get(filename=filename)
            except History.DoesNotExist:
                media_to_transfer.append(filename)
        return media_to_transfer

    @property
    def validate_dump(self):
        TODAY = datetime.today().strftime("%Y%m%d")
        all_files = self.user_tx_files + self.archived_tx_files
        for filename in all_files:
            if TODAY in filename:
                return True
        return False

    @property
    def archived_tx_files(self):
        client, message = self.connect_localhost()
        self.log_message(message, "info")
        localhost = client.open_sftp()
        file_names = localhost.listdir(self.user_archived_tx_files)
        localhost.close()
        return file_names

    @property
    def send_transactions_to_server(self):
        try:
            server, message = self.connect_to_remote_server()
            self.log_message(message, "info")
            if server:
                sftp_server = server.open_sftp()
                send_transactions_to_server_status = []
                for file_name in self.user_tx_files:
                    local_file_name = self.user_dump_tx_files + '/{}'.format(file_name)
                    remote_file_name = self.remote_dump_tx_files + '/{}'.format(file_name)
                    sftp_server.put(local_file_name, remote_file_name)  # Transfer transaction to the server
                    if self.check_remote_file_status(sftp_server, remote_file_name):  # Confirm it has transferred
                        client, message = self.connect_localhost()
                        self.log_message(message, "info")
                        self.archive_file(client, self.user_dump_tx_files, local_file_name, self.user_archived_tx_files)
                        self.create_history(file_name)
                        send_transactions_to_server_status.append(True)
                    else:
                        send_transactions_to_server_status.append(False)
                        message = "Transaction: {}, failed to transfer. {}.".format(file_name, datetime.today())
                        self.log_message(message, "error")
                        raise IOError(message)
                return send_transactions_to_server_status
        except IOError as e:
            print(e)
            raise("{}".format(e))
        return False

    @property
    def send_media_files_to_server(self):
        """ if the media file does not exists in the server then it will be transferred to the server.
        """
        try:
            server, message = self.connect_to_remote_server()
            self.log_message(message, "info")
            sftp_server = server.open_sftp()
            local_media_transfer_status = []
            for file_name in self.user_media_files_to_transfer:
                local_file_name = self.user_media_files + '/{}'.format(file_name)
                remote_file_name = self.remote_user_media_files + '/{}'.format(file_name)
                sftp_server.put(local_file_name, remote_file_name, confirm=True)  # Transfer media file to the server
#                 self.create_history(file_name)
                if self.check_remote_file_status(sftp_server, remote_file_name):
                    self.create_history(file_name)
                    local_media_transfer_status.append(True)
                else:
                    print("Not working")
                    raise ("Media file: {} failed to transfer. {}".format(file_name, datetime.today()))
            sftp_server.close()
            return local_media_transfer_status
        except IOError:
            raise IOError("failed to send file {}".format(file_name))
        return False

    def create_history(self, filename):
        history = History.objects.create(
            location=self.location,
            remote_path=self.remote_dump_tx_files,
            archive_path=self.user_archived_tx_files,
            filename=filename,
            acknowledged=True,
            ack_datetime=datetime.today(),
        )
        print ("")
        return history

    def check_remote_file_status(self, sftp, remote_file_name):
        try:
            sftp.stat(remote_file_name)
            return True
        except IOError as e:
            print("{}".format(e))
            return False

    def archive_file(self, client, transfered_file_dir, filename, archive_dir):
        stdin, stdout, stderr = client.exec_command(
            "cd {} ; mv {} {}".format(transfered_file_dir, filename, archive_dir))
        return (stdin, stdout, stderr)

    @property
    def archived_media(self):
        client = self.connect_localhost()
        sftp = client.open_sftp()
        file_names = sftp.listdir(self.archived_media_dir)
        client.close()
        return file_names

    def count_media_sent(self, filenames):
        return History.objects.filter(filename__in=filenames).count()

    def count_tx_sent(self, filenames):
        return History.objects.filter(filename__in=filenames).count()

    def log_message(self, message, message_type):
        if message_type == "error":
            logger.error(message)
        elif message_type == "info":
            logger.info(message)
        else:
            logger.debug(message)
