import json
import logging
import socket

from django.apps import apps as django_apps
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView

from edc_base.view_mixins import EdcBaseViewMixin
from edc_sync_files.action_handler import ActionHandler, ActionHandlerError

from ..admin import edc_sync_admin
from ..edc_sync_view_mixin import EdcSyncViewMixin
from ..site_sync_models import site_sync_models

app_config = django_apps.get_app_config('edc_sync_files')
logger = logging.getLogger('edc_sync')


class HomeView(EdcBaseViewMixin, EdcSyncViewMixin, TemplateView):

    template_name = 'edc_sync/home.html'
    action_handler_cls = ActionHandler

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._action_handler = None

    @property
    def action_handler(self):
        if not self._action_handler:
            self._action_handler = self.action_handler_cls(
                src_path=app_config.outgoing_folder,
                dst_path=app_config.incoming_folder,
                archive_path=app_config.archive_folder,
                username=app_config.user,
                remote_host=app_config.remote_host)
        return self._action_handler

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        app_config = django_apps.get_app_config('edc_sync')
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
            pending_files=self.action_handler.pending_filenames,
            recently_sent_files=self.action_handler.sent_history[0:20],
            site_models=site_sync_models.site_models)
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.is_ajax():
            action = request.GET.get('action')
            try:
                self.action_handler.action(label=action)
            except ActionHandlerError as e:
                logger.warn(e)
                logger.exception(e)
                response_data = dict(errmsg=str(e))
            else:
                response_data = self.action_handler.data
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
