from django.db import models

from edc_sync.models import SyncModelMixin
from edc_base.model.models import BaseUuidModel


class TestItem(SyncModelMixin, BaseUuidModel):

    test_item_identifier = models.CharField(max_length=35, unique=True)

    comment = models.CharField(max_length=50, null=True)
    # history = AuditTrail()

    class Meta:
        app_label = 'sync'
        db_table = 'bhp_sync_testitem'
