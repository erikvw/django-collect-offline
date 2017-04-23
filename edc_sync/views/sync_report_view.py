from edc_base.view_mixins import EdcBaseViewMixin

from django.apps import apps as django_apps
from django.db.models.aggregates import Count
from django.views.generic.base import TemplateView

from edc_sync_files.models import UploadTransactionFile

from ..admin import edc_sync_admin
from ..edc_sync_view_mixin import EdcSyncViewMixin
from ..models import IncomingTransaction


class SyncReportView(EdcBaseViewMixin, EdcSyncViewMixin, TemplateView):

    template_name = 'edc_sync/sync_report.html'

    @property
    def report_data(self):
        report_data = {}
        qs = IncomingTransaction.objects.values('producer').filter(
            is_consumed=False).annotate(Count('is_consumed')).order_by('producer')
        for item in qs:
            producer = item.get('producer')
            report_data.update({producer: {
                'total_not_consumed': item.get('is_consumed__count'),
                'upload_transaction_file': UploadTransactionFile.objects.filter(
                    producer=producer).order_by('-created').last()}})
        return report_data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        app_config = django_apps.get_app_config('edc_sync')
        context.update(
            edc_sync_admin=edc_sync_admin,
            project_name=context.get(
                'project_name') + ': ' + self.role.title(),
            base_template_name=app_config.base_template_name,
            report_data=self.report_data)
        return context
