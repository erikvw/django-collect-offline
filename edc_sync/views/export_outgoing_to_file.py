import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.utils import timezone

from edc_device import Device

from ..utils import export_outgoing_transactions


@login_required
def export_outgoing_to_file(request, path, target_name=None):
    """A view to call function export_outgoing_transactions."""
    target_name = target_name or 'folder'
    device = Device()
    path = path or os.path.join('/tmp', '{}{}_outgoing_{}.json'.format(
        settings.APP_NAME, str(device), str(timezone.now().strftime("%Y%m%d%H%M"))))
    try:
        exported = export_outgoing_transactions(path)
        messages.add_message(request, messages.SUCCESS, (
            'Exported {} outgoing transactions to {}.').format(exported, path))
    except IOError:
        # TODO: possible to get here??
        messages.add_message(request, messages.ERROR, (
            'Unable to find or access {} \'{}\'').format(target_name, '/'.join(path.split('/')[:-1])))
    url = reverse('section_index_url', kwargs={'selected_section': 'administration'})
    return redirect(url)
