from django.db import models


class HostManager(models.Manager):

    def get_by_natural_key(self, hostname, port):
        return self.get(hostname=hostname, port=port)


class HistoryManager(models.Manager):

    def get_by_natural_key(self, filename, sent_datetime):
        return self.get(filename=filename, sent_datetime=sent_datetime)
