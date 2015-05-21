from edc.base.model.tests.factories import BaseUuidModelFactory
from edc.device.sync.models import Producer


class ProducerFactory(BaseUuidModelFactory):
    FACTORY_FOR = Producer

    name = 'dispatch_destination'
    settings_key = 'dispatch_destination'
    url = 'http://'
