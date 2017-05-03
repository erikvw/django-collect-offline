import json
import os

from django.http.response import HttpResponse
from django.views.generic.base import TemplateView
from edc_base.view_mixins import EdcBaseViewMixin

# from edc_sync_files.transaction import (
#     DumpToUsb, TransactionLoadUsbFile, transaction_messages)

from ..edc_sync_view_mixin import EdcSyncViewMixin


class DumpToUsbView(EdcBaseViewMixin, EdcSyncViewMixin, TemplateView):

    pass
#     def get(self, request, *args, **kwargs):
#         context = self.get_context_data(**kwargs)
#         transaction_messages.clear()
#         response_data = {
#             'error': False,
#             'messages': transaction_messages.messages()}
#         if request.is_ajax():
#             if request.GET.get('action') == 'check_usb_connection':
#                 if os.path.exists('/Volumes/BCPP'):
#                     response_data.update({'error': False})
#                 else:
#                     transaction_messages.add_message(
#                         'error', 'USB not connected. Please connect BCPP USB.',
#                         network=True)
#                     response_data.update({
#                         'error': True,
#                         'messages': transaction_messages.messages(),
#                         'error_message': 'USB not connected. Please connect BCPP USB.'})
#             elif request.GET.get('action') == 'dump_to_usb':
#                 usb_dump = DumpToUsb()
#                 if usb_dump.is_dumped_to_usb:
#                     response_data = {
#                         'error': False,
#                         'filename': usb_dump.filename,
#                         'messages': transaction_messages.messages()}
#                 else:
#                     response_data = {
#                         'error': True,
#                         'messages': transaction_messages.messages()}
#             elif request.GET.get('action') == 'load_json_file':
#                 usb_file = TransactionLoadUsbFile()
#                 if usb_file.is_usb_transaction_file_loaded:
#                     response_data = {
#                         'error': False,
#                         'messages': transaction_messages.messages(),
#                         'usb_files': usb_file.usb_files}
#                 else:
#                     response_data = {
#                         'error': False,
#                         'usb_files': usb_file.usb_files,
#                         'messages': transaction_messages.messages()}
#             return HttpResponse(json.dumps(response_data), content_type='application/json')
#         return self.render_to_response(context)
