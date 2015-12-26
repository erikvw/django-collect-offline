import socket
import logging
from django.conf import settings


logger = logging.getLogger(__name__)


class NullHandler(logging.Handler):
    def emit(self, record):
        pass
nullhandler = logger.addHandler(NullHandler())


class TransactionProducer(object):
    """Stores and returns a derived producer name of hostname-database_name from
    the host (without domain name) and settings.DATABASES['default'].

    Database name comes from either OPTIONS or NAME."""
    def __init__(self):
        hostname = socket.gethostname().split('.')[0]
        if not hostname:
            raise TypeError('Unable to determine the hostname of this host.')
        try:
            # OPTIONS takes precedence over NAME
            cnf = settings.DATABASES.get('default').get('OPTIONS').get('read_default_file')
            with open(cnf, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if 'database' in line:
                        database_name = line.split('=')[1].strip()
                        break
        except (KeyError, TypeError):
            database_name = settings.DATABASES.get('default').get('NAME')
        if not database_name:
            raise TypeError('Unable to determine the \'default\' database name of this django project.')
        self.producer_name = '{}-{}'.format(
            hostname.lower(),
            database_name.lower())[:50]

    def __repr__(self):
        return 'TransactionProducer({0.producer_name!r})'.format(self)

    def __str__(self):
        return self.producer_name or ''

transaction_producer = str(TransactionProducer())
