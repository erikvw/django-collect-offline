from edc_base.model_managers import HistoricalRecords
from edc_base.model_mixins.list_model_mixin import ListModelMixin
from uuid import uuid4

from django.db import models
from django.db.models.deletion import PROTECT
from edc_base.model_mixins import BaseUuidModel, BaseModel
from edc_base.utils import get_utcnow
from simple_history.models import HistoricalRecords as BadHistoricalRecords


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
        return (self.f1,)


class TestModelDates(BaseUuidModel):

    f1 = models.CharField(max_length=10, unique=True)

    f2 = models.DateField(
        blank=True,
        null=True)

    f3 = models.DateTimeField(
        blank=True,
        default=get_utcnow)

    objects = TestModelManager()

    def natural_key(self):
        return (self.f1,)


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
        return (self.f1,)


class YetAnotherBadTestModel(BaseUuidModel):
    """A test model with the wrong HistoricalManager.
    """

    f1 = models.CharField(max_length=10, default='f1')

    objects = TestModelManager()

    history = BadHistoricalRecords()  # missing UUID handling

    def natural_key(self):
        return (self.f1,)


class TestOfflineModelNoHistoryManager(BaseUuidModel):
    """A test model without a HistoricalManager.
    """

    f1 = models.CharField(max_length=10, default='f1')

    objects = TestModelManager()

    def natural_key(self):
        return (self.f1,)


class TestOfflineModelNoUuid(BaseModel):
    """A test model without a HistoricalManager.
    """

    f1 = models.CharField(max_length=10, default='f1')

    objects = TestModelManager()

    def natural_key(self):
        return (self.f1,)


class M2m(ListModelMixin, BaseUuidModel):

    pass


class TestModelWithFkProtected(BaseUuidModel):

    f1 = models.CharField(max_length=10, unique=True)

    test_model = models.ForeignKey(TestModel, on_delete=PROTECT)

    objects = TestModelManager()

    history = HistoricalRecords()

    def natural_key(self):
        return (self.f1,)
    natural_key.dependencies = ['django_collect_offline.test_model']


class TestModelWithM2m(BaseUuidModel):

    f1 = models.CharField(max_length=10, unique=True)

    m2m = models.ManyToManyField(M2m)

    objects = TestModelManager()

    history = HistoricalRecords()

    def natural_key(self):
        return (self.f1,)
