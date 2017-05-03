from edc_sync_files.transaction import transaction_messages

from .models import IncomingTransaction


class Consumer(object):

    def __init__(self, transactions=None, using=None, model_name=None,
                 verbose=None, producer_name=None, check_hostname=None,
                 check_device=None):
        self.model_name = model_name
        self.producer_name = producer_name
        self.using = using or 'default'
        self.verbose = True if verbose is None else verbose
        self.transactions = transactions or []
        self.check_hostname = check_hostname
        self.check_device = check_device

    def consume(self, model_name=None, producer_name=None, **kwargs):
        """Consumes ALL incoming transactions on \'using\' in
           order by ('producer', 'timestamp').
        """
        consumed = 0
        if model_name and not producer_name:
            incoming_transactions = IncomingTransaction.objects.using(
                self.using).filter(
                is_consumed=False,
                is_ignored=False,
                tx_name=model_name).order_by('timestamp', 'producer')
        elif producer_name and not model_name:
            incoming_transactions = IncomingTransaction.objects.using(
                self.using).filter(
                is_consumed=False,
                is_ignored=False,
                producer=producer_name).order_by('timestamp', 'producer')
        elif producer_name and model_name:
            incoming_transactions = IncomingTransaction.objects.using(
                self.using).filter(
                is_consumed=False,
                is_ignored=False,
                tx_name=model_name,
                producer=producer_name).order_by('timestamp', 'producer')
        else:
            incoming_transactions = IncomingTransaction.objects.using(
                self.using).filter(
                is_consumed=False,
                is_ignored=False,
                tx_pk__in=self.transactions).order_by('timestamp', 'producer')
        total_incoming_transactions = incoming_transactions.count()
        for index, incoming_transaction in enumerate(incoming_transactions):
            if self.verbose:
                action = ''
                print('{0} / {1} {2} {3}'.format(index + 1,
                                                 total_incoming_transactions,
                                                 incoming_transaction.producer,
                                                 incoming_transaction.tx_name))
                print('    tx_pk=\'{0}\''.format(incoming_transaction.tx_pk))
                action = 'failed'
            try:
                if incoming_transaction.deserialize_transaction(
                        check_hostname=self.check_hostname,
                        check_device=self.check_device):
                    action = 'saved'
                    consumed += 1
            except ValueError as e:
                action = 'failed'
                message = 'Failed to play transaction. Got {}'.format(str(e))
                transaction_messages.add_message('error', message)
            if self.verbose:
                print('    {0}'.format(action))
        return consumed
