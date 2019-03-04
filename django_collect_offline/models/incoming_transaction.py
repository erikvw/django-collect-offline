from django.contrib.sites.models import Site
from django.db import models
from edc_model.models import BaseUuidModel
from edc_sites.models import CurrentSiteManager, SiteModelMixin

from ..model_mixins import TransactionModelMixin


class IncomingTransaction(TransactionModelMixin, SiteModelMixin, BaseUuidModel):

    """ Transactions received from a remote host.
    """

    site = models.ForeignKey(Site, on_delete=models.CASCADE, null=True, editable=False)

    is_consumed = models.BooleanField(default=False)

    is_self = models.BooleanField(default=False)

    on_site = CurrentSiteManager()

    objects = models.Manager()

    class Meta:
        ordering = ["timestamp"]
