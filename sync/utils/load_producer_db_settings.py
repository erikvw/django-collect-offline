from django.conf import settings

from ..models import Producer
from edc.device.sync.exceptions import ProducerError


def load_producer_db_settings(producer_name=None, refresh=None):
    """Updates the settings.DATABASES dictionary with the connections to the
    producer databases for setting_keys that do already exist.

    Raise a ProducerError exception if the producer does not exist or producer details
    are incomplete.

    TODO: the producer attributes should be confirmed, eg hostname, IP, password. etc."""
    if producer_name:
        try:
            producer = Producer.objects.get(settings_key=producer_name, is_active=True)
            producers = [producer]
        except Producer.DoesNotExist:
            return ('Unable to update settings key for Producer \'{}\'. Producer does '
                    'not exist or is not active (is_active=False).'.format(producer_name))
    else:
        producers = Producer.objects.filter(is_active=True)
    if not producers:
        return None
    for producer in producers:
        if (producer.db_user_name is None or producer.db_user is None or
                producer.db_password is None or producer.producer_ip is None or
                producer.settings_key is None):
            raise ProducerError('Producer {} is incorrectly defined in model Producer. '
                                'Please correct or set is_active=False. Got settings_key={} '
                                'db_name={} db_user={} db_password={} producer_ip={}'.format(
                                    producer.name,
                                    producer.settings_key,
                                    producer.db_user_name,
                                    producer.db_user,
                                    '*****' if producer.db_password else None,
                                    producer.producer_ip))
        if not settings.DATABASES.get(producer.settings_key, None):
            settings.DATABASES[producer.settings_key] = {
                'ENGINE': 'django.db.backends.mysql',
                'OPTIONS': {
                    'init_command': 'SET storage_engine=INNODB',
                },
                'NAME': producer.db_user_name,
                'USER': producer.db_user,
                'PASSWORD': producer.db_password,
                'HOST': producer.producer_ip,
                'PORT': producer.port,
            }
    return "Added {0} Producers to settings.DATABASE.".format(len(producers))
