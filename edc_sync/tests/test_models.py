from django.db import models

from edc_sync.models import SyncModelMixin
from edc_base.model.models import BaseUuidModel
from edc_base.audit_trail import AuditTrail


class TestModelManager(models.Manager):

    def get_by_natural_key(self, f1):
        return self.get(f1=f1)


class TestModel(SyncModelMixin, BaseUuidModel):

    f1 = models.CharField(max_length=10, unique=True)

    objects = TestModelManager()

    history = AuditTrail()

    def natural_key(self):
        return (self.f1, )

    class Meta:
        app_label = 'edc_sync'
