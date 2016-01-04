from django.db import models

from edc_sync.models import SyncModelMixin
from edc_base.model.models import BaseUuidModel
from edc_base.audit_trail import AuditTrail
from edc_base.model.models.base_list_model import BaseListModel


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


class M2m(SyncModelMixin, BaseListModel):

    class Meta:
        app_label = 'edc_sync'


class FkManager(models.Manager):

    def get_by_natural_key(self, name):
        print('get_by_natural_key={}'.format(self._db))
        return self.get(name=name)


class Fk(SyncModelMixin, BaseUuidModel):

    name = models.CharField(max_length=10, unique=True)

    objects = FkManager()

    def natural_key(self):
        return (self.name, )

    class Meta:
        app_label = 'edc_sync'


class ComplexTestModelManager(models.Manager):

    def get_by_natural_key(self, f1, fk):
        return self.get(f1=f1, fk=fk)


class ComplexTestModel(SyncModelMixin, BaseUuidModel):

    f1 = models.CharField(max_length=10)

    fk = models.ForeignKey(Fk)

    m2m = models.ManyToManyField(M2m, null=True)

    objects = ComplexTestModelManager()

    history = AuditTrail()

    def natural_key(self):
        return (self.f1, ) + self.fk.natural_key()
    natural_key.dependencies = ['edc_sync.fk']

    class Meta:
        app_label = 'edc_sync'
        unique_together = ('f1', 'fk')
