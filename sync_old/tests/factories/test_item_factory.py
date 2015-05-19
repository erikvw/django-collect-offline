from edc.base.model.tests.factories import BaseUuidModelFactory
from edc.device.sync.models import TestItem


class TestItemFactory(BaseUuidModelFactory):
    FACTORY_FOR = TestItem
