from django.test import TestCase
from django.apps import apps as django_apps
from django.test.utils import tag


from edc_example.models import TestModel
from edc_sync_files.classes import TransactionFile
from edc_sync.models import OutgoingTransaction
from edc_sync_files.models.upload_transaction_file import UploadTransactionFile


from ..utils.transaction_tx_pk import previous_tx_pk_and_next_tx_pk


@tag('TestTransactionFileUploader')
class TestTransactionFileUploader(TestCase):

    def setUp(self):
        self.edc_sync_files_app = django_apps.get_app_config('edc_sync_files')

    def test_transaction_file_valid_for_upload(self):
        # Create transactions
        TestModel.objects.using('client').create(f1='erik20')
        TestModel.objects.using('client').create(f1='setsiba20')

        # Dump transaction
        path = self.edc_sync_files_app.destination_folder
        transaction_file = TransactionFile(path, hostname='010')
        outgoing_transactions = OutgoingTransaction.objects.using('client').filter(
            is_consumed_server=False)

        previous_tx_pk, next_tx_pk = previous_tx_pk_and_next_tx_pk(using='client')

        transaction_file.export_to_json(
            transactions=outgoing_transactions, hostname='010',
            previous_tx_pk=previous_tx_pk,
            current_tx_pk=next_tx_pk,
            using='client')

        upload_file_count = UploadTransactionFile.objects.using('client').all().count()
        self.assertGreater(upload_file_count, 0)
