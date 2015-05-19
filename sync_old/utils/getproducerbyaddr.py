import re
import socket

from edc.device.sync.exceptions import ProducerError


def getproducerbyaddr(producer):
    try:
        hostname, aliases, ips = socket.gethostbyaddr(producer.producer_ip)
    except AttributeError:
        raise AttributeError(('Expected a producer instance. Got producer=\'{}\'.').format(producer.__class__))
    except (socket.gaierror, socket.herror):
        if not re.match(r'^[1-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$', producer.producer_ip):
            raise ProducerError(
                'Invalid IP for producer {}. Got {}'.format(producer.name, producer.producer_ip))
        raise ProducerError((
            'Cannot find producer hostname {} using IP={}. Please confirm both that the '
            'the IP address and hostname in the Producer model are available '
            'in DNS or the server\'s hosts file.').format(producer.name, producer.producer_ip))
    return hostname, aliases, ips
