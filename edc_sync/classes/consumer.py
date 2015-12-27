from __future__ import print_function

from django.db.models import get_model

from ..exceptions import TransactionConsumerError
from ..models import OutgoingTransaction, IncomingTransaction


class Consumer(object):

    def __init__(self, model_name, producer_name, using, check_hostname=None, lock_name=None):
        self.model_name = model_name
        self.producer_name = producer_name
        self.using = using or 'default'
        self.check_hostname = True if check_hostname is None else check_hostname
        self.lock_name = lock_name  # used??
        self._incoming_transactions = None

    def fetch_outgoing(self, using_source, using_destination=None):
        """Fetches all OutgoingTransactions not consumed from a source
        and saves them locally (default).

        This is a db2Db connection

            Args:
                using_source: DATABASE key for the database with
                    the OutgoingTransactions
                using_destination: DATABASE key for the database
                    receiving the IncoingTransactions. (default=default)"""
        if not using_destination:
            using_destination = 'default'
        if using_source == using_destination:
            raise TransactionConsumerError('Cannot fetch outgoing transactions from myself')
#         OutgoingTransaction = get_model('sync', 'OutgoingTransaction')
#         IncomingTransaction = get_model('sync', 'IncomingTransaction')
        for outgoing_transaction in OutgoingTransaction.objects.using(using_source).filter(is_consumed=False):
            new_incoming_transaction = IncomingTransaction()
            # copy outgoing attr into new incoming
            for field in OutgoingTransaction._meta.fields:
                if field.attname not in ['id', 'is_consumed']:
                    setattr(new_incoming_transaction, field.attname, getattr(outgoing_transaction, field.attname))
            new_incoming_transaction.is_consumed = False
            # save incoming on destination
            new_incoming_transaction.save(using=using_destination)
            outgoing_transaction.is_consumed = True
            # update outgoing on source
            outgoing_transaction.save(using=using_source)
