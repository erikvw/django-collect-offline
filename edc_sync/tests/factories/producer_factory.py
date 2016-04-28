import factory

from edc_sync.models import Producer


class ProducerFactory(factory.DjangoModelFactory):
    class Meta:
        model = Producer

    name = 'dispatch_destination'
    settings_key = 'dispatch_destination'
    url = 'http://'
