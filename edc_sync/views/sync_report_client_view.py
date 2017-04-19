import json

from edc_base.view_mixins import EdcBaseViewMixin

from django.views.generic.base import TemplateView
from django.apps import apps as django_apps

from edc_sync_files.classes import SyncReportClient

from ..edc_sync_view_mixin import EdcSyncViewMixin
from ..admin import edc_sync_admin
from edc_sync.models import ReceiveDevice
from django.http.response import HttpResponse


class SyncReportClientView(
        EdcBaseViewMixin, EdcSyncViewMixin, TemplateView):

    template_name = 'edc_sync/sync_report_client.html'

    def __init__(self, *args, **kwargs):
        super(SyncReportClientView, self).__init__(*args, **kwargs)

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
        report = SyncReportClient()
        context = self.get_context_data(**kwargs)
        context.update({'report_data': report.report_data})
        if request.is_ajax():
            action = request.GET.get('action')
            response_data = {}
            if action == 'receive':
                ReceiveDevice.objects.create(
                    hostname=request.GET.get('hostname'),
                    received_by=request.user,
                    sync_files=json.dumps(report.synced_files(
                        request.GET.get('hostname'))))
                return HttpResponse(
                    json.dumps(response_data), content_type='application/json')
        return self.render_to_response(context)
