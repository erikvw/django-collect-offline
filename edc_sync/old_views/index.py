import socket

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext

from ..models import Producer, OutgoingTransaction


@login_required
def index(request, **kwargs):
    selected_producer = kwargs.get('selected_producer', None)
    producers = Producer.objects.filter(is_active=True)
    return render_to_response('sync.html', {
        'producers': producers,
        'producer_cls': Producer,
        'outgoingtransaction_cls': OutgoingTransaction,
        'hostname': socket.gethostname(),
        'selected_producer': selected_producer
    }, context_instance=RequestContext(request))
