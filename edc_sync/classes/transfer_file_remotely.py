import paramiko
import getpass
import os
from unipath import Path
from edc_sync.models import History
from datetime import datetime
from django.conf import settings


class TransferFileRemotely(object):
    """
    ADD TO SETTINGS FILES

    COMMUNITY = 'Gaborone'

    TX_DUMP_PATH = "path_to_dump_files"  # e.g ~/transaction_json_files/dump
    TX_ARCHIVE_DIR = "path_to_achive_tx_files"

    REMOTE_SERVER_IP = 'IP'  # e.g edc4 IP
    MEDIA_REMOTE_DIR = 'remote_path_where_media_files_will_transfer_to'
    MEDIA_DIR = "path_to_where_you_kept_media_files"

    REMOTE_DIR = "remote_path_to_transfer_files_to"  # e.g ~/transaction_json_files/to_upload
    REMOTE_USERNAME = "enter_remote_username"
    REMOTE_PASSWORD = "enter_remote_password"

    CLIENT_PASSWORD = "localhost_password"

    """
    def __init__(self, remote_server_ip=None, remote_dir=None, remote_username=None, remote_password=None,
                 tx_dump_dir=None, media_dir=None, media_remote_dir=None, archive_dir=None,
                 client_password=None, archived_media_dir=None):
        self.remote_server_ip = remote_server_ip or settings.REMOTE_SERVER_IP
        self.remote_dir = remote_dir or settings.REMOTE_DIR
        self.remote_username = remote_username or settings.REMOTE_USERNAME
        self.remote_password = remote_password or settings.REMOTE_PASSWORD
        self.tx_dump_dir = tx_dump_dir or settings.TX_DUMP_PATH
        self.media_dir = media_dir or settings.MEDIA_DIR
        self.media_remote_dir = media_remote_dir or settings.MEDIA_REMOTE_DIR
        self.archive_dir = archive_dir or settings.ARCHIVE_DIR
        self.client_password = client_password or settings.CLIENT_PASSWORD
        self.client_remote = None
        self.community = settings.COMMUNITY
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.archived_files_no = 0

    def connect_localhost(self):
        try:
            self.client.connect('localhost', username=getpass.getuser(), password=self.client_password)
        except paramiko.SSHException as e:
            raise ("Please contact administrator, Connection Error occurred.({})".format(e))
        return self.client

    def connect_to_remote_server(self):
        try:
            self.client_remote = paramiko.SSHClient()
            self.client_remote.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client_remote.connect(self.remote_server_ip, username=self.remote_username,
                                       password=self.remote_password)
        except paramiko.SSHException as e:
            raise ("Please contact administrator, Connection Error occurred.({})".format(e))
        return self.client_remote

    @property
    def local_tx_files(self):
        client = self.connect_localhost()
        sftp = client.open_sftp()
        file_names = sftp.listdir(self.tx_dump_dir)
        client.close()
        return file_names

    @property
    def local_media_files(self):
        client = self.connect_localhost()
        sftp = client.open_sftp()
        filenames = sftp.listdir(self.media_dir)
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
        all_files = self.local_tx_files + self.archived_tx_files
        for filename in all_files:
            if TODAY in filename:
                return True
        return False

    @property
    def archived_tx_files(self):
        client = self.connect_localhost()
        sftp = client.open_sftp()
        file_names = sftp.listdir(self.archive_dir)
        client.close()
        return file_names

    @property
    def send_transactions_to_server(self):
        try:
            server = self.connect_to_remote_server()
            sftp_server = server.open_sftp()
            send_transactions_to_server_status = []
            for file_name in self.local_tx_files:
                local_file_name = self.tx_dump_dir + '/{}'.format(file_name)
                remote_file_name = self.remote_dir + '/{}'.format(file_name)
                sftp_server.put(local_file_name, remote_file_name)
                if self.check_remote_file_status(sftp_server, remote_file_name):
                    send_transactions_to_server_status.append(True)
                    client = self.connect_localhost()
                    self.archive_file(client, self.tx_dump_dir, local_file_name, self.archive_dir)
                    self.create_history(file_name)
                else:
                    send_transactions_to_server_status.append(False)
            return send_transactions_to_server_status
        except IOError as e:
            print(e)
            raise("{}".format(e))
        return False

    def create_history(self, filename):
        history = History.objects.create(
            community=self.community,
            remote_hostname=self.remote_server_ip,
            remote_path=self.remote_dir,
            archive_path=self.archive_dir,
            filename=filename,
            acknowledged=True,
            ack_datetime=datetime.today(),
        )
        print(history.__dict__)
        return history

    @property
    def send_media_files_to_server(self):
        """ if the media file does not exists in the server then it will be transferred to the server.
        """
        try:
            server = self.connect_to_remote_server()
            sftp_server = server.open_sftp()
            local_media_transfer_status = []
            for file_name in self.local_media_files:
                local_file_name = self.media_dir + '/{}'.format(file_name)
                remote_file_name = self.media_remote_dir + '/{}'.format(file_name)
                if self.check_remote_file_status(sftp_server, file_name):
                    local_media_transfer_status.append(False)
                else:
                    sftp_server.put(local_file_name, remote_file_name)
                    if self.check_remote_file_status(sftp_server, file_name):
                        self.create_history(file_name)
                    local_media_transfer_status.append(True)
            return local_media_transfer_status
        except IOError:
            return False
        return False

    def check_remote_file_status(self, sftp, remote_file_name):
        try:
            sftp.stat(remote_file_name)
            return True
        except IOError:
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
