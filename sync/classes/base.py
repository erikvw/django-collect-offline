import logging
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)


class NullHandler(logging.Handler):
    def emit(self, record):
        pass
nullhandler = logger.addHandler(NullHandler())


class Base(object):

    def __init__(self, using=None):
        self._using = None
        self._set_using(using)

    def _set_using(self, value=None):
        """Sets the using parameter for this machine, almost always a server.

        Args:
            value: valid settings DATABASE key. (default: default)

        """
        if not value:
            value = 'default'
        self._using = value
        self.verify_using(value)

    def get_using(self):
        if not self._using:
            self._set_using()
        return self._using

    def verify_using(self, value):
        if value not in settings.DATABASES.keys():
            raise ImproperlyConfigured('Cannot find key "{0}" in settings.DATABASES.'.format(value))
        return True
