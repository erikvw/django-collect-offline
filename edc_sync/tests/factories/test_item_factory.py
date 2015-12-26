import factory

from edc.device.sync.models import TestItem


class TestItemFactory(factory.DjangoModelFactory):
    class Meta:
        model = TestItem
