from django.conf import settings

from edc.device.sync.exceptions import ProducerError


def update_producer_from_settings(producer=None):
    """Updates a given \'producer instance\' with values from settings.DATABASES."""
    Producer = producer.__class__
    try:
        producer = Producer.objects.get(settings_key=producer.settings_key, is_active=True)
        if not settings.DATABASES.get(producer.settings_key, None):
            raise ProducerError('Unable to update Producer \'{}\', Settings key \'{}\' '
                                'does not exist.'.format(producer.name, producer.settings_key))
        cnf = settings.DATABASES.get(producer.settings_key).get('OPTIONS').get('read_default_file')
        with open(cnf, 'r') as f:
            lines = f.readlines()
            producer.producer_ip = None
            producer.url = None
            for line in lines:
                if 'database' in line:
                    producer.db_user_name = line.split('=')[1].strip()
                elif 'user' in line:
                    producer.db_user = line.split('=')[1].strip()
                elif 'password' in line:
                    producer.db_password = line.split('=')[1].strip()
                elif 'host' in line:
                    producer.producer_ip = line.split('=')[1].strip() or '127.0.0.1'
            if not producer.producer_ip:
                producer.producer_ip = settings.DATABASES.get(producer.settings_key).get('HOST') or '127.0.0.1'
            producer.url = 'http://{}/'.format(producer.producer_ip)
        producer.save()
    except (KeyError, TypeError):
        producer.db_user_name = settings.DATABASES.get(producer.settings_key).get('NAME')
        producer.db_user = settings.DATABASES.get(producer.settings_key).get('USER')
        producer.db_password = settings.DATABASES.get(producer.settings_key).get('PASSWORD')
        producer.producer_ip = settings.DATABASES.get(producer.settings_key).get('HOST') or '127.0.0.1'
        producer.save()
    except Producer.DoesNotExist:
        raise ProducerError('Unable to update Producer \'{}\'. Producer is not '
                            'active (is_active=False).'.format(producer))
    return Producer.objects.get(pk=producer.pk)
