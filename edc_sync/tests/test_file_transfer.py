import os
import json

from django.conf import settings
from django.test.testcases import TestCase
from edc_sync.classes.file_transfer import FileTransfer, FileConnector
from edc_sync.constants import LOCALHOST, REMOTE
from edc_sync.models.history import History


class TestFileTransfer(TestCase):

    def setUp(self):
        self.transfer = FileTransfer()
        self.file_server_folder = os.path.join(settings.BASE_DIR, "tests", "media", "file_server_folder")
        self.media_dir = os.path.join(settings.BASE_DIR, "tests", "media", "upload")

    def test_connect_to_localhost(self):
        """Assert  Connection to localhost """
        self.assertTrue(self.transfer.connect_to_device(LOCALHOST))

    def test_connect_to_remote_device(self):
        """ Assert Connection to remote machine """
        self.assertTrue(self.transfer.connect_to_device(REMOTE))

    def test_count_media_to_send(self):
        """ Assert how many media files to send base on history table."""
        sent_media = ['media_a.png', 'media_b.png']
        for filename in sent_media:
            FileConnector(filename=filename).create_history()
        self.assertEqual(History.objects.all().count(), 2)
        media_dir = [self.media_dir]
        transfer = FileTransfer(media_dir=media_dir)
        json.dumps(transfer.pending_media_files())
        required_files = transfer.pending_media_files()[0].get('required_files')
        self.assertEqual(["media_c.png"], required_files)

    def test_count_on_media_transfer(self):
        """ Assert how many media files to send base on history table."""
        sent_media = ['media_a', 'media_b']
        localhost_media_files = ['media_a', 'media_b', 'media_c', 'media_d']
        media_to_transfer = []
        for filename in localhost_media_files:
            if filename in sent_media:
                continue
            media_to_transfer.append(filename)
        self.assertEqual(len(media_to_transfer), 2)
        for f in ['media_c', 'media_d']:
            self.assertIn(f, media_to_transfer)
#
#         sent_media = ['media_a', 'media_b', 'media_c']
#         localhost_media_files = ['media_a', 'media_b', 'media_c', 'media_d']
#         media_to_transfer = []
#         for filename in localhost_media_files:
#             if filename in sent_media:
#                 continue
#             media_to_transfer.append(filename)
#         self.assertEqual(media_to_transfer, 1)
# 
#         for f in ['media_d']:
#             self.assertIn(f, media_to_transfer)
# 
#     def test_count_media_sent(self):
#         media_count = 5
#         sent = 3
#         initial = media_count - sent

        #         for filename in sent_media:
#             transfer.create_history(filename)
#         self.assertEqual(History.objects.all().count(), 2)
# 
#         initial_count = len(transfer.local_media_files)


