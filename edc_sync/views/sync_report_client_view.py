import json
import requests

from datetime import datetime

from django.urls import reverse
from django.apps import apps as django_apps
from django.http.response import HttpResponse
from django.views.generic.base import TemplateView
from requests.exceptions import ConnectionError, HTTPError

from edc_base.view_mixins import EdcBaseViewMixin
from edc_sync_files.models import ImportedTransactionFileHistory

from ..admin import edc_sync_admin
from ..edc_sync_view_mixin import EdcSyncViewMixin
from ..models import SyncConfirmation, Client


class SyncReportClientView(
        EdcBaseViewMixin, EdcSyncViewMixin, TemplateView):

    template_name = 'edc_sync/sync_report_client.html'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        app_config = django_apps.get_app_config('edc_map')
        context.update(
            edc_sync_admin=edc_sync_admin,
            project_name=context.get(
                'project_name') + ': ' + self.role.title(),
            base_template_name=app_config.base_template_name)
        return context

    def get(self, request, *args, **kwargs):
        report = Report()
        context = self.get_context_data(**kwargs)
        context.update({'report_data': report.report_data})
        if request.is_ajax():
            action = request.GET.get('action')
            response_data = {}
            if action == 'receive':
                SyncConfirmation.objects.create(
                    hostname=request.GET.get('hostname'),
                    received_by=request.user,
                    sync_files=json.dumps(report.synced_files(
                        request.GET.get('hostname'))))
                return HttpResponse(
                    json.dumps(response_data), content_type='application/json')
        return self.render_to_response(context)


class Report:
    """ Displays number of pending transactions in the client and number of
        times the machine have synced.
    """

    def __init__(self):
        self.report_data = []

        for client in Client.objects.all():
            try:
                SyncConfirmation.objects.get(
                    hostname=client.hostname,
                    received_date=datetime.today().date())
                received = True
            except SyncConfirmation.DoesNotExist:
                received = False
            try:
                url = 'http://' + client.hostname + reverse(
                    'edc_sync:transaction-count')
                r = requests.get(url, timeout=3)
                data = r.json()
                connected = True
            except (ConnectionError, Exception):
                pending = -1
                connected = False
            except HTTPError:
                pending = -1
                connected = True
            else:
                pending = data.get('outgoingtransaction_count')
            data = {'device': client.hostname,
                    'sync_times': self.synced_files(client.hostname),
                    'pending': pending,
                    'connected': connected,
                    'received': received,
                    'comment': client.comment}  # FIXME include number of pending files.
            self.report_data.append(data)

    def synced_files(self, hostname):
        producer = '{}-default'.format(hostname)
        return [p for p in ImportedTransactionFileHistory.objects.filter(
            producer=producer,
            created__date=datetime.today().date()).order_by('-created')]
