

class PendingTransactionError(Exception):
    pass


class SerializationTransactionError(Exception):
    pass


class TransactionConsumerError(Exception):
    pass


class SyncError(Exception):
    pass


class SyncDeserializationError(Exception):
    pass


class SyncModelError(Exception):
    pass


class SyncProducerError(Exception):
    pass


class UsingError(Exception):
    pass


class UsingSourceError(Exception):
    pass


class UsingDestinationError(Exception):
    pass


class RegistryNotLoaded(Exception):
    pass


class AlreadyRegistered(Exception):
    pass
