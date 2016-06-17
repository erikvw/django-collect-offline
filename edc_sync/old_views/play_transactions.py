import socket

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.shortcuts import redirect

from ..classes import Consumer

# TODO: imported from bcpp, cleanup, make class based view


@login_required
def play_transactions(request, **kwargs):
    """ Play all the incoming transactions pending on the server."""
    consumer = Consumer()
    consumer.consume()
    message = consumer.get_consume_feedback()
    messages.add_message(request, messages.INFO, message)
    try:
        if settings.EMAIL_AFTER_CONSUME:
            send_mail('{} incoming transactions'.format(str(socket.gethostname())),
                      message,
                      settings.EMAIL_HOST_USER + '@bhp.org.bw',
                      ['django@bhp.org.bw'],
                      fail_silently=False)
    except AttributeError:
        pass
    url = reverse('bcpp_sync_url')
    return redirect(url)
