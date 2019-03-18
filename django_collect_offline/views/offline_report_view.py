from django.apps import apps as django_apps
from django.db.models.aggregates import Count
from django.views.generic import ListView
from django_collect_offline_files.admin_site import django_collect_offline_files_admin
from edc_dashboard.view_mixins import EdcViewMixin

from ..offline_view_mixin import OfflineViewMixin
from ..models import IncomingTransaction


class OfflineReportView(EdcViewMixin, OfflineViewMixin, ListView):

    template_name = "django_collect_offline/offline_report.html"

    def get_queryset(self):
        return (
            IncomingTransaction.objects.values("producer")
            .filter(is_consumed=False)
            .annotate(pending=Count("is_consumed"))
            .order_by("producer")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        app_config = django_apps.get_app_config("django_collect_offline")
        context.update(
            base_template_name=app_config.base_template_name,
            django_collect_offline_files_admin=django_collect_offline_files_admin,
        )
        return context
