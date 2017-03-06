import os

from django.test.testcases import TestCase
from django.test.utils import tag
from django.conf import settings
from faker import Faker
from edc_example.models import TestModel
from edc_sync_files.classes import TransactionFile
from edc_sync.models import OutgoingTransaction
from ..utils.transaction_tx_pk import previous_tx_pk_and_next_tx_pk


@tag('TestUploadTransactions')
class TestUploadTransactions(TestCase):

    def setUp(self):
        self.fake = Faker()

    @tag('test_export_to_json_file')
    def test_export_to_json_file(self):
        # Create transactions

        TestModel.objects.using('client').create(f1=self.fake.name())
        TestModel.objects.using('client').create(f1=self.fake.name())

        # Dump transaction
        path = settings.MEDIA_ROOT
        transaction_file = TransactionFile(path, hostname='010')

        outgoing_transactions = OutgoingTransaction.objects.using('client').filter(
            is_consumed_server=False)

        self.assertGreater(outgoing_transactions.count(), 0)

        exported_no, is_exported, _ = transaction_file.export_to_json(
            transactions=outgoing_transactions, hostname='010',
            using='client')
        self.assertTrue(is_exported)
        self.assertGreater(exported_no, 0)

        outgoing_transactions_count = OutgoingTransaction.objects.using('client').filter(
            is_consumed_server=False).count()
        self.assertEqual(outgoing_transactions_count, 0)

    @tag('test_upload_transaction_file_valid')
    def test_upload_transaction_file_valid_first_timeupload(self):
        # Create transactions
        TestModel.objects.using('client').create(f1=self.fake.name())
        TestModel.objects.using('client').create(f1=self.fake.name())

        # Dump transaction
        path = settings.MEDIA_ROOT
        transaction_file = TransactionFile(path, hostname='010')
        outgoing_transactions = OutgoingTransaction.objects.using('client').filter(
            is_consumed_server=False)

        previous_tx_pk, next_tx_pk = previous_tx_pk_and_next_tx_pk(using='client')

        transaction_file.export_to_json(
            transactions=outgoing_transactions, hostname='010',
            previous_tx_pk=previous_tx_pk,
            current_tx_pk=next_tx_pk,
            using='client')
        new_file_to_upload = TransactionFile(path=transaction_file.path)

        self.assertTrue(new_file_to_upload.valid)

    @tag('test_upload_transaction_file_valid2')
    def test_upload_transaction_file_valid_next_file_same(self):
        # Create transactions
        TestModel.objects.using('client').create(f1=self.fake.name())
        TestModel.objects.using('client').create(f1='baba')

        # Dump transaction
        path = settings.MEDIA_ROOT
        transaction_file = TransactionFile(path, hostname='010')
        outgoing_transactions = OutgoingTransaction.objects.using('client').filter(
            is_consumed_server=False)

        previous_tx_pk, next_tx_pk = previous_tx_pk_and_next_tx_pk(using='client')

        transaction_file.export_to_json(
            transactions=outgoing_transactions, hostname='010',
            previous_tx_pk=previous_tx_pk,
            current_tx_pk=next_tx_pk,
            using='client')
        new_file_to_upload = TransactionFile(path=transaction_file.path)
        self.assertTrue(new_file_to_upload.upload())

        new_file_to_upload = TransactionFile(path=transaction_file.path)
        self.assertFalse(new_file_to_upload.valid)

    @tag('test_upload_transaction_file_valid1')
    def test_upload_transaction_file_valid_next_file(self):
        # Create transactions
        TestModel.objects.using('client').create(f1=self.fake.name())
        TestModel.objects.using('client').create(f1=self.fake.name())

        # Dump transaction
        path = settings.MEDIA_ROOT
        transaction_file = TransactionFile(path, hostname='010')
        outgoing_transactions = OutgoingTransaction.objects.using('client').filter(
            is_consumed_server=False)

        previous_tx_pk, next_tx_pk = previous_tx_pk_and_next_tx_pk(using='client')

        transaction_file.export_to_json(
            transactions=outgoing_transactions, hostname='010',
            previous_tx_pk=previous_tx_pk,
            current_tx_pk=next_tx_pk,
            using='client')
        new_file_to_upload = TransactionFile(path=transaction_file.path)
        self.assertTrue(new_file_to_upload.upload())

        TestModel.objects.using('client').create(f1=self.fake.name())
        TestModel.objects.using('client').create(f1=self.fake.name())

        # Dump transaction
        path = settings.MEDIA_ROOT
        transaction_file = TransactionFile(path, hostname='010')
        outgoing_transactions = OutgoingTransaction.objects.using('client').filter(
            is_consumed_server=False)

        previous_tx_pk, next_tx_pk = previous_tx_pk_and_next_tx_pk(using='client')

        transaction_file.export_to_json(
            transactions=outgoing_transactions, hostname='010',
            previous_tx_pk=previous_tx_pk,
            current_tx_pk=next_tx_pk,
            using='client')

        new_file_to_upload = TransactionFile(path=transaction_file.path)
        self.assertTrue(new_file_to_upload.valid)

    @tag('test_file_upload')
    def test_file_upload(self):
        # Create transactions
        TestModel.objects.using('client').create(f1='erik20')
        TestModel.objects.using('client').create(f1='setsiba20')

        # Dump transaction
        path = settings.MEDIA_ROOT
        transaction_file = TransactionFile(path, hostname='010')
        outgoing_transactions = OutgoingTransaction.objects.using('client').filter(
            is_consumed_server=False)

        previous_tx_pk, next_tx_pk = previous_tx_pk_and_next_tx_pk(using='client')

        transaction_file.export_to_json(
            transactions=outgoing_transactions, hostname='010',
            previous_tx_pk=previous_tx_pk,
            current_tx_pk=next_tx_pk,
            using='client')
        new_file_to_upload = TransactionFile(path=transaction_file.path)
        self.assertTrue(new_file_to_upload.valid)
        self.assertTrue(new_file_to_upload.upload())
