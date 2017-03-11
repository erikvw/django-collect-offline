import os
from django.conf import settings
from django.core import serializers
from django.db import transaction

from edc_base.utils import get_utcnow
from edc_sync_files.classes import transaction_messages

from ..models import OutgoingTransaction


def export_outgoing_transactions(path, hostname=None):
    """Serializes OutgoingTransactions to a file from a netbook to the MIDDLEMAN.

    * Updates transactions as consumed by the middleman (is_consumed_middleman = True).
    * In this case storage used, e.g.USB or local file, are considered to be a MIDDLEMAN.
    """
    export_outgoing_transactions = True
    exported = 0
    is_consumed_middleman_count = 0
    filename = '{}_{}.json'.format(
        hostname,
        str(get_utcnow().strftime("%Y%m%d%H%M")))
    path = os.path.join(path, filename) or os.path.join('/tmp', filename)
    try:
        with open(path, 'w') as f:
            outgoing_transactions = OutgoingTransaction.objects.filter(
                is_consumed_server=False)
            json_txt = serializers.serialize(
                "json", outgoing_transactions,
                ensure_ascii=True, use_natural_foreign_keys=True,
                use_natural_primary_keys=False)
            f.write(json_txt)
            exported = outgoing_transactions.count()
            with transaction.atomic():
                outgoing_transactions.update(
                    is_consumed_server=True,
                    consumer='/'.join(path.split('/')[:-1]),
                    consumed_datetime=get_utcnow())
            is_consumed_middleman_count = exported
    except IOError as io_error:
        message = (
            'Unable to create or write to file \'{}\'. '
            'Got {}').format(path, str(io_error))
        transaction_messages.add_message(
            'error', message, network=False, permission=False)
        export_outgoing_transactions = False
    transaction_messages.add_message(
        'success', 'dumped transaction file successfully',
        network=False, permission=False)
    return export_outgoing_transactions
    return exported, is_consumed_middleman_count
