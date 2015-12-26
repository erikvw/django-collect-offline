import socket
from django.conf import settings


class TransactionProducer(object):
    """Stores and returns a derived producer name of hostname-database_name from
    the host (without domain name) and settings.DATABASES['default'].

    Database name comes from either OPTIONS or NAME."""
    def __init__(self):
        self._database_name = None
        hostname = socket.gethostname().split('.')[0]
        try:
            self.producer_name = '{}-{}'.format(hostname.lower(), self.database_name.lower())
        except AttributeError:
            raise AttributeError('Unable to determine the \'producer\' name')

    def __repr__(self):
        return 'TransactionProducer({0.producer_name!r})'.format(self)

    def __str__(self):
        return self.producer_name or ''

    @property
    def database_name(self):
        if not self._database_name:
            try:
                cnf = settings.DATABASES.get('default').get('OPTIONS').get('read_default_file')
                with open(cnf, 'r') as f:
                    lines = f.readlines()
                    for line in lines:
                        if 'database' in line:
                            self._database_name = line.split('=')[1].strip()
                            break
            except (KeyError, TypeError):
                self._database_name = settings.DATABASES.get('default').get('NAME')
        return self._database_name.lower()

transaction_producer = str(TransactionProducer())
