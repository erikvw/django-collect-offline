from uuid import uuid4

from django.db import models

from edc_base.model_managers import HistoricalRecords
from edc_base.model_mixins import BaseUuidModel
from edc_base.model_mixins.list_model_mixin import ListModelMixin
from django.db.models.deletion import PROTECT


class TestModelManager(models.Manager):

    def get_by_natural_key(self, f1):
        return self.get(f1=f1)


class TestModel(BaseUuidModel):

    f1 = models.CharField(max_length=10, unique=True)

    f2 = models.CharField(max_length=10, null=True)

    f3 = models.CharField(max_length=10, default=uuid4())

    objects = TestModelManager()

    history = HistoricalRecords()

    def natural_key(self):
        return (self.f1, )


class BadTestModel(BaseUuidModel):
    """A test model that is missing natural_key and get_by_natural_key.
    """

    f1 = models.CharField(max_length=10, default='f1')

    objects = models.Manager()


class AnotherBadTestModel(BaseUuidModel):
    """A test model that is missing get_by_natural_key.
    """

    f1 = models.CharField(max_length=10, default='f1')

    objects = models.Manager()

    def natural_key(self):
        return (self.f1, )


class M2m(ListModelMixin, BaseUuidModel):

    pass


class TestModelWithFkProtected(BaseUuidModel):

    f1 = models.CharField(max_length=10, unique=True)

    test_model = models.ForeignKey(TestModel, on_delete=PROTECT)

    objects = TestModelManager()

    history = HistoricalRecords()

    def natural_key(self):
        return (self.f1, )


class TestModelWithM2m(BaseUuidModel):

    f1 = models.CharField(max_length=10, unique=True)

    m2m = models.ManyToManyField(M2m)

    objects = TestModelManager()

    history = HistoricalRecords()

    def natural_key(self):
        return (self.f1, )
