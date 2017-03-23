import json

from edc_base.view_mixins import EdcBaseViewMixin

from django.views.generic.base import TemplateView
from django.apps import apps as django_apps

from edc_sync_files.classes import SyncReport

from ..edc_sync_view_mixin import EdcSyncViewMixin
from ..admin import edc_sync_admin
from django.http.response import HttpResponse


class SyncReportDetailedView(
        EdcBaseViewMixin, EdcSyncViewMixin, TemplateView):

    template_name = 'edc_sync/sync_report_detailed.html'

    def __init__(self, *args, **kwargs):
        self.all_machines = False
        super(SyncReportDetailedView, self).__init__(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(context.get('producer'))
        app_config = django_apps.get_app_config('edc_map')
        context.update(
            edc_sync_admin=edc_sync_admin,
            project_name=context.get(
                'project_name') + ': ' + self.role.title(),
            base_template_name=app_config.base_template_name)
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        print(kwargs.get('producer'))
        response_data = {}
        if request.is_ajax():
            report_data = []
            report = SyncReport(
                all_machines=False, producer=kwargs.get('producer'))
            for data in report.report_data:
                transaction_file = data.get('upload_transaction_file')
                file_time = transaction_file.file_name.split('-')[0]
                file_time = file_time.split('.')
                file_time = file_time[:2] + ':' + file_time[2:4]
                data.update(
                    {'y': file_time,
                     'barColors': ['#15B25F', '#B21516']})
                del data['upload_transaction_file']
                report_data.append(report_data)
            response_data.update(report=report_data)
            return HttpResponse(json.dumps(response_data),
                                content_type='application/json')
        context.update({
            'report_data': self.report_data})
        return self.render_to_response(context)
