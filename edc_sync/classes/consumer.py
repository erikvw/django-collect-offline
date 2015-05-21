from ..exceptions import TransactionConsumerError

from ..models import OutgoingTransaction, IncomingTransaction


class Consumer(object):

    def __init__(self, allow_from_self=None):
        self.allow_from_self = allow_from_self

    def fetch_outgoing(self, using_source, using_destination=None):
        """Fetches all OutgoingTransactions not consumed from source and
        saves to destination (using).

        Args:
            using_source: database with the OutgoingTransactions
            using_destination: database receiving transactions to be saved as incoming.
                (default: None /'default')"""
        if using_source == using_destination and not self.allow_from_self:
            raise TransactionConsumerError('Cannot fetch outgoing transactions from myself')
        for outgoing_transaction in OutgoingTransaction.objects.using(using_source).filter(is_consumed=False):
            incoming_transaction = IncomingTransaction()
            values = {'is_consumed': False}
            for field in OutgoingTransaction._meta.fields:
                if field.name not in ['id', 'is_consumed_server', 'is_consumed_middleman']:
                    values.update({field.name: getattr(outgoing_transaction, field.name)})
            incoming_transaction = IncomingTransaction(**values)
            incoming_transaction.save(using=using_destination)
            incoming_transaction.to_model_instance(using_destination, check_hostname=True)
            outgoing_transaction.is_consumed = True
            outgoing_transaction.save(using=using_source)
