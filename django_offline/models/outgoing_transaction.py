from django.contrib.sites.models import Site
from django.db import models
from edc_base.model_mixins import BaseUuidModel
from edc_base.sites import CurrentSiteManager, SiteModelMixin
from edc_base.utils import get_utcnow

from .model_mixins import TransactionModelMixin


class OutgoingTransaction(TransactionModelMixin, SiteModelMixin, BaseUuidModel):

    """ Transactions produced locally to be consumed/sent
    to a queue or consumer.
    """

    site = models.ForeignKey(
        Site, on_delete=models.CASCADE, null=True, editable=False)

    is_consumed_middleman = models.BooleanField(
        default=False)

    is_consumed_server = models.BooleanField(
        default=False)

    using = models.CharField(max_length=25, null=True)

    on_site = CurrentSiteManager()

    objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.using:
            raise ValueError(
                'Value for \'{}.using\' cannot be None.'.format(
                    self._meta.model_name))
        if self.is_consumed_server and not self.consumed_datetime:
            self.consumed_datetime = get_utcnow()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['timestamp']
