from edc_base.view_mixins import EdcBaseViewMixin

from django.apps import apps as django_apps
from django.db.models.aggregates import Count
from django.views.generic import ListView

from edc_sync_files.admin_site import edc_sync_files_admin

from ..offline_view_mixin import OfflineViewMixin
from ..models import IncomingTransaction


class OfflineReportView(EdcBaseViewMixin, OfflineViewMixin, ListView):

    template_name = 'django_offline/offline_report.html'

    def get_queryset(self):
        return IncomingTransaction.objects.values('producer').filter(
            is_consumed=False).annotate(
                pending=Count('is_consumed')).order_by('producer')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        app_config = django_apps.get_app_config('django_offline')
        context.update(
            base_template_name=app_config.base_template_name,
            edc_sync_files_admin=edc_sync_files_admin)
        return context
