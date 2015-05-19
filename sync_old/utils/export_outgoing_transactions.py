import os

from datetime import datetime

from django.core import serializers
from django.db import transaction

from ..models import OutgoingTransaction


def export_outgoing_transactions(path):
    """Serializes OutgoingTransactions to a file from a netbook to the
    MIDDLEMAN and updates transactions as consumed by the middleman
    (is_consumed_middleman = True). In this case storage used which might
    be a USB or local file system are considered to be a MIDDLEMAN."""
    exported = 0
    path = path or os.path.join('/tmp', 'edc_tx_{}.json'.format(str(datetime.now().strftime("%Y%m%d%H%M"))))
    try:
        with open(path, 'w') as f:
            outgoing_transactions = OutgoingTransaction.objects.filter(
                is_consumed_server=False, is_consumed_middleman=False)
            json_txt = serializers.serialize(
                "json", outgoing_transactions, ensure_ascii=True, use_natural_keys=True)
            f.write(json_txt)
            exported = outgoing_transactions.count()
        is_consumed_middleman_count = 0
        with transaction.atomic():
            for outgoing_transaction in outgoing_transactions:
                outgoing_transaction.is_consumed_middleman = True
                outgoing_transaction.consumer = '/'.join(path.split('/')[:-1])
                outgoing_transaction.consumed_datetime = datetime.now()
                outgoing_transaction.save()
                is_consumed_middleman_count += 1
    except IOError as io_error:
        raise IOError(('Unable to create or write to file \'{}\'. Got {}').format(path, str(io_error)))
    return exported, is_consumed_middleman_count
