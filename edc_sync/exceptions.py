

class PendingTransactionError(Exception):
    pass


class SerializationTransactionError(Exception):
    pass


class TransactionConsumerError(Exception):
    pass


class SyncError(Exception):
    pass


class UsingError(Exception):
    pass


class UsingSourceError(Exception):
    pass


class UsingDestinationError(Exception):
    pass
