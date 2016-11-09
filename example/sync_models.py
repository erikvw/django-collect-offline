from django.db import models

from django_crypto_fields.crypt_model_mixin import CryptModelMixin
from django_crypto_fields.fields import EncryptedCharField
from edc_base.model.models import BaseUuidModel
from edc_base.model.models.list_model_mixin import ListModelMixin
from edc_sync.model_mixins import SyncModelMixin, SyncHistoricalRecords


class Crypt(CryptModelMixin, SyncModelMixin, BaseUuidModel):

    class Meta:
        app_label = 'edc_example'
        unique_together = (('hash', 'algorithm', 'mode'),)


class BadTestModel(SyncModelMixin, BaseUuidModel):
    """A test model that is missing natural_key and get_by_natural_key."""

    f1 = models.CharField(max_length=10, default='f1')

    objects = models.Manager()

    class Meta:
        app_label = 'edc_example'


class AnotherBadTestModel(SyncModelMixin, BaseUuidModel):
    """A test model that is missing get_by_natural_key."""

    f1 = models.CharField(max_length=10, default='f1')

    objects = models.Manager()

    def natural_key(self):
        return (self.f1, )

    class Meta:
        app_label = 'edc_example'


class TestModelManager(models.Manager):

    def get_by_natural_key(self, f1):
        return self.get(f1=f1)


class TestModel(SyncModelMixin, BaseUuidModel):

    f1 = models.CharField(max_length=10, unique=True)

    objects = TestModelManager()

    history = SyncHistoricalRecords()

    def natural_key(self):
        return (self.f1, )

    class Meta:
        app_label = 'edc_example'


class TestModelProxy(TestModel):

    class Meta:
        app_label = 'edc_example'
        proxy = True


class TestEncryptedModel(SyncModelMixin, BaseUuidModel):

    f1 = models.CharField(max_length=10, unique=True)

    encrypted = EncryptedCharField(max_length=10, unique=True)

    objects = TestModelManager()

    history = SyncHistoricalRecords()

    def natural_key(self):
        return (self.f1, )

    class Meta:
        app_label = 'edc_example'


class M2m(SyncModelMixin, ListModelMixin, BaseUuidModel):

    class Meta:
        app_label = 'edc_example'


class FkManager(models.Manager):

    def get_by_natural_key(self, name):
        return self.get(name=name)


class Fk(SyncModelMixin, BaseUuidModel):

    name = models.CharField(max_length=10, unique=True)

    objects = FkManager()

    def natural_key(self):
        return (self.name, )

    class Meta:
        app_label = 'edc_example'


class ComplexTestModelManager(models.Manager):

    def get_by_natural_key(self, f1, fk):
        return self.get(f1=f1, fk=fk)


class ComplexTestModel(SyncModelMixin, BaseUuidModel):

    f1 = models.CharField(max_length=10)

    fk = models.ForeignKey(Fk)

    m2m = models.ManyToManyField(M2m)

    objects = ComplexTestModelManager()

    history = SyncHistoricalRecords()

    def natural_key(self):
        return (self.f1, ) + self.fk.natural_key()
    natural_key.dependencies = ['example.fk']

    class Meta:
        app_label = 'edc_example'
        unique_together = ('f1', 'fk')
