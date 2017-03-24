import json

from edc_base.view_mixins import EdcBaseViewMixin

from django.views.generic.base import TemplateView
from django.apps import apps as django_apps

from edc_sync_files.classes import SyncReportDetail

from ..edc_sync_view_mixin import EdcSyncViewMixin
from ..admin import edc_sync_admin


class SyncReportDetailedView(
        EdcBaseViewMixin, EdcSyncViewMixin, TemplateView):

    template_name = 'edc_sync/sync_report_detailed.html'

    def __init__(self, *args, **kwargs):
        self.all_machines = False
        super(SyncReportDetailedView, self).__init__(*args, **kwargs)

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
        context = self.get_context_data(**kwargs)
        report = SyncReportDetail(
            producer=kwargs.get('producer_name'))
        context.update({
            'report_data': report.report_data,
            'transactions_files': report.transactions_files})
        return self.render_to_response(context)
