import sys

from django.conf import settings

from .client import Client
from .history import History
from .incoming_transaction import IncomingTransaction
from .outgoing_transaction import OutgoingTransaction
from .server import Server

if 'django_collect_offline' in settings.APP_NAME and 'makemigrations' not in sys.argv:
    from ..tests import models
