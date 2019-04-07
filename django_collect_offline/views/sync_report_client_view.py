import requests

from datetime import datetime
from django.apps import apps as django_apps
from django.urls import reverse
from django.views.generic.base import TemplateView
from edc_dashboard.view_mixins import EdcViewMixin
from django_collect_offline_files.models import ImportedTransactionFileHistory
from requests.exceptions import ConnectionError, HTTPError

from ..admin import django_collect_offline_admin
from ..offline_view_mixin import OfflineViewMixin
from ..models import Client


class SyncReportClientView(EdcViewMixin, OfflineViewMixin, TemplateView):

    template_name = "django_collect_offline/sync_report_client.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        app_config = django_apps.get_app_config("edc_map")  # FIXME: ?
        context.update(
            django_collect_offline_admin=django_collect_offline_admin,
            project_name=context.get("project_name") + ": " + self.role.title(),
            base_template_name=app_config.base_template_name,
        )
        return context

    def get(self, request, *args, **kwargs):
        report = Report()
        context = self.get_context_data(**kwargs)
        context.update({"report_data": report.report_data})
        if request.is_ajax():
            action = request.GET.get("action")
            # response_data = {}
            if action == "receive":
                # TODO: see TransactionExporterViewMixin
                raise TypeError()
        #                 response_data = dict(
        #                     confirm=True, hostname=sync_confirm.confirm_code)
        #                 return HttpResponse(
        # json.dumps(response_data), content_type='application/')
        return self.render_to_response(context)


class Report:
    """ Displays number of pending transactions in the client and number of
    times the machine have synced.
    """

    imported_history_model = ImportedTransactionFileHistory

    def __init__(self):
        self.report_data = []
        for client in Client.objects.all():
            try:
                self.history_model.objects.get(
                    hostname=client.hostname, confirmed_date=datetime.today().date()
                )  # ????
                received = True
            except self.history_model.DoesNotExist:
                received = False
            try:
                url = (
                    "http://"
                    + client.hostname
                    + reverse("django_collect_offline:transaction-count")
                )
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
                pending = data.get("outgoingtransaction_count")
                pending_files_no = data.get("pending_files_no")
            data = {
                "device": client.hostname,
                "sync_times": self.synced_files(client.hostname),
                "pending": pending,
                "connected": connected,
                "received": received,
                "pending_files_no": pending_files_no,
                "comment": client.comment,
            }
            self.report_data.append(data)

    def synced_files(self, hostname):
        producer = f"{hostname}-default"
        return [
            p
            for p in self.imported_history_model.objects.filter(
                producer=producer, created__date=datetime.today().date()
            ).order_by("-created")
        ]
