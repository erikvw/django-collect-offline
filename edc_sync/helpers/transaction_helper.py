import socket

from django.db.models import Q

from ..models import OutgoingTransaction, IncomingTransaction

from ..exceptions import PendingTransactionError


class TransactionHelper(object):

    def has_incoming_for_producer(self, producer, using=None):
        """Returns True if there are incoming transactions from the
        producer in this host.

        ..note:: at the moment, Audit transactions are being ignored.
        """
        using = using or 'default'
        # TODO: figure out how to consume the Audit transactions so
        #       that they do not have to be excluded.
        return IncomingTransaction.objects.using(using).filter(
            producer=producer, is_consumed=False).exclude(
                Q(is_ignored=True) | Q(tx_name__contains='Audit')).exists()

    def has_incoming_for_model(self, models, using=None):
        """Checks if incoming transactions exist for the given model(s).
            models is a list of instance object names"""
        using = using or 'default'
        if not models:
            return False
        if not isinstance(models, (list, tuple)):
            models = [models]
        return IncomingTransaction.objects.using(using).filter(
            tx_name__in=models, is_consumed=False).exclude(is_ignored=True).exists()

    def has_outgoing(self, using=None):
        using = using or 'default'
        return OutgoingTransaction.objects.using(using).filter(
            is_consumed_server=False, is_consumed_middleman=False).exists()

    def has_outgoing_for_producer(self, hostname, using, return_queryset=None, raise_exception=None):
        """Returns True if there are Outgoing Transactions in the database (using)
        created by the host (hostname) where is_consumed_server=False,
        is_consumed_middleman=False and are not set to be ignored (is_ignored=False).

            * look for OutgoingTransactions on a me (Default):
                  hostname = my hostname as from gethostname()
                  using = 'default'
            * look for OutgoingTransactions on a remote machine (e.g. a producer):
                  hostname = producer hostname as from gethostname() on
                             the producer (if that can be done);
                  using = producer.name or settings.DATABASES key for the producer;
            * look for OutgoingTransactions on a remote machine created by
              another host (e.g. server):
                  hostname = server hostname as from gethostname();
                  using = producer.name or settings.DATABASES key for the machine;
        """
        hostname = hostname or socket.gethostname()
        using = using or 'default'
        return_queryset = return_queryset or False
        raise_exception = raise_exception or False
        if return_queryset:
            outgoing_transactions = OutgoingTransaction.objects.using(using).filter(
                hostname_modified=hostname,
                is_consumed_server=False,
                is_consumed_middleman=False,
                is_ignored=False
                )
            if outgoing_transactions and raise_exception:
                raise PendingTransactionError('Host \'{}\' has {} pending transactions. '
                                              'Please correct before continuing. (using={})'.format(
                                                  hostname, outgoing_transactions.count(), using))
            return outgoing_transactions
        has_outgoing_transactions = OutgoingTransaction.objects.using(using).filter(
            hostname_modified=hostname,
            is_consumed_server=False,
            is_consumed_middleman=False,
            is_ignored=False
            ).exists()
        if has_outgoing_transactions and raise_exception:
            raise PendingTransactionError('Host {} has pending transactions. '
                                          'Please correct before continuing. (using={})'.format(hostname, using))
        return has_outgoing_transactions

    def outgoing_transactions(self, hostname, using, raise_exception=None):
        """Returns a queryset of OutgoingTransactions as determined by method
        :func:`has_outgoing_for_producer`.

        Args: hostname, using, raise_exception=None"""
        using = using or 'default'
        raise_exception = raise_exception or False
        return self.has_outgoing_for_producer(hostname, using, return_queryset=True,
                                              raise_exception=raise_exception)
