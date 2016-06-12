from django.db import models

from django_crypto_fields.fields import EncryptedCharField
from django_crypto_fields.crypt_model_mixin import CryptModelMixin
from edc_sync.models import SyncHistoricalRecords as AuditTrail
# from simple_history.models import HistoricalRecords as AuditTrail
from edc_base.model.models import BaseUuidModel
from edc_sync.models import SyncModelMixin
from edc_base.model.models.list_model_mixin import ListModelMixin
from edc_base.model.models.base_model import BaseModel


class Crypt(CryptModelMixin, SyncModelMixin, BaseUuidModel):

    class Meta:
        app_label = 'example'
        unique_together = (('hash', 'algorithm', 'mode'),)


class BadTestModel(SyncModelMixin, BaseUuidModel):
    """A test model that is missing natural_key and get_by_natural_key."""

    f1 = models.CharField(max_length=10, default='f1')

    objects = models.Manager()

    class Meta:
        app_label = 'example'


class AnotherBadTestModel(SyncModelMixin, BaseUuidModel):
    """A test model that is missing get_by_natural_key."""

    f1 = models.CharField(max_length=10, default='f1')

    objects = models.Manager()

    def natural_key(self):
        return (self.f1, )

    class Meta:
        app_label = 'example'


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
        app_label = 'example'


class TestModelProxy(TestModel):

    class Meta:
        app_label = 'example'
        proxy = True


class TestEncryptedModel(SyncModelMixin, BaseUuidModel):

    f1 = models.CharField(max_length=10, unique=True)

    encrypted = EncryptedCharField(max_length=10, unique=True)

    objects = TestModelManager()

    history = AuditTrail()

    def natural_key(self):
        return (self.f1, )

    class Meta:
        app_label = 'example'


class M2m(ListModelMixin, BaseModel):

    class Meta:
        app_label = 'example'


class FkManager(models.Manager):

    def get_by_natural_key(self, name):
        return self.get(name=name)


class Fk(SyncModelMixin, BaseUuidModel):

    name = models.CharField(max_length=10, unique=True)

    objects = FkManager()

    def natural_key(self):
        return (self.name, )

    class Meta:
        app_label = 'example'


class ComplexTestModelManager(models.Manager):

    def get_by_natural_key(self, f1, fk):
        return self.get(f1=f1, fk=fk)


class ComplexTestModel(SyncModelMixin, BaseUuidModel):

    f1 = models.CharField(max_length=10)

    fk = models.ForeignKey(Fk)

    m2m = models.ManyToManyField(M2m)

    objects = ComplexTestModelManager()

    history = AuditTrail()

    def natural_key(self):
        return (self.f1, ) + self.fk.natural_key()
    natural_key.dependencies = ['example.fk']

    class Meta:
        app_label = 'example'
        unique_together = ('f1', 'fk')
