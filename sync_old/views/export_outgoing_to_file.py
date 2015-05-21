import os

from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import redirect

from edc.device import device

from ..utils import export_outgoing_transactions


@login_required
def export_outgoing_to_file(request, path, target_name=None):
    """A view to call function export_outgoing_transactions."""
    app_name = settings.APP_NAME
    target_name = target_name or 'folder'
    path = path or os.path.join('/tmp', '{}{}_outgoing_{}.json'.format(
        app_name, str(device), str(datetime.now().strftime("%Y%m%d%H%M"))))
    try:
        exported, consumed_by_middleman = export_outgoing_transactions(path)
        messages.add_message(request, messages.SUCCESS, (
            'Exported {} outgoing transactions to {}.').format(exported, path))
        messages.add_message(request, messages.SUCCESS, (
            'Set {} outgoing transactions as consumed by MIDDLEMAN.').format(consumed_by_middleman))
    except IOError:
        messages.add_message(request, messages.ERROR, (
            'Unable to find or access {} \'{}\'').format(target_name, '/'.join(path.split('/')[:-1])))
    url = reverse('section_index_url', kwargs={'selected_section': 'administration'})
    return redirect(url)
