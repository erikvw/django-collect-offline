import json
import socket

from django.apps import apps as django_apps
from django.conf import settings

from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView


from edc_base.view_mixins import EdcBaseViewMixin
from edc_sync_files.constants import CONFIRM_BATCH, PENDING_FILES
from edc_sync_files.view_mixins import TransactionExporterViewMixin, TransactionFileSenderViewMixin
from edc_sync_files.view_actions import ViewActions

from ..admin import edc_sync_admin
from ..edc_sync_view_mixin import EdcSyncViewMixin
from ..site_sync_models import site_sync_models


class HomeView(EdcBaseViewMixin, EdcSyncViewMixin, TransactionExporterViewMixin,
               TransactionFileSenderViewMixin, TemplateView):

    template_name = 'edc_sync/home.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        app_config = django_apps.get_app_config('edc_sync')
        view_actions = ViewActions()
        context.update(
            base_template_name=app_config.base_template_name,
            cors_origin_whitelist=self.cors_origin_whitelist,
            edc_sync_admin=edc_sync_admin,
            edc_sync_app_config=app_config,
            edc_sync_files_app_config=django_apps.get_app_config(
                'edc_sync_files'),
            edc_sync_role=self.role,
            hostname=socket.gethostname(),
            ip_address=django_apps.get_app_config(
                'edc_sync_files').remote_host,
            pending_files=view_actions.pending_filenames,
            recently_sent_files=view_actions.recently_sent_files,
            site_models=site_sync_models.site_models)
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.is_ajax():
            action = request.GET.get('action')
            view_actions = ViewActions()
            if action in [view_actions.actions]:
                response_data = view_actions.action(name=action)
            elif action == CONFIRM_BATCH:
                files = request.GET.get('files')
                for filename in (files or []).split(','):
                    self.confirm_batch(filename=filename)
            return HttpResponse(
                json.dumps(response_data), content_type='application/json')
        return self.render_to_response(context)

    @property
    def cors_origin_whitelist(self):
        try:
            cors_origin_whitelist = settings.CORS_ORIGIN_WHITELIST
        except AttributeError:
            cors_origin_whitelist = []
        return cors_origin_whitelist
