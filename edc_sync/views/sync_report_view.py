from edc_base.view_mixins import EdcBaseViewMixin

from django.views.generic.base import TemplateView
from django.apps import apps as django_apps

from edc_sync_files.classes import SyncReport

from ..edc_sync_view_mixin import EdcSyncViewMixin
from ..admin import edc_sync_admin


class SyncReportView(
        EdcBaseViewMixin, EdcSyncViewMixin, TemplateView):

    template_name = 'edc_sync/sync_report.html'

    def __init__(self, *args, **kwargs):
        super(SyncReportView, self).__init__(*args, **kwargs)

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
        report = SyncReport(all_machines=True)
        context = self.get_context_data(**kwargs)
        context.update({
            'report_data': report.report_data})
        return self.render_to_response(context)
