import json
import socket

from django.apps import apps as django_apps
from django.conf import settings

from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView


from edc_base.view_mixins import EdcBaseViewMixin
from edc_sync_files.file_transfer import TransactionFileSender
from edc_sync_files.view_mixins import TransactionExporterViewMixin

from ..admin import edc_sync_admin
from ..edc_sync_view_mixin import EdcSyncViewMixin
from ..site_sync_models import site_sync_models

from paramiko.ssh_exception import (
    BadHostKeyException, AuthenticationException, SSHException)


class HomeView(EdcBaseViewMixin, EdcSyncViewMixin, TransactionExporterViewMixin, TemplateView):

    template_name = 'edc_sync/home.html'
    transaction_file_sender = TransactionFileSender

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        app_config = django_apps.get_app_config('edc_sync')
        context.update(
            edc_sync_admin=edc_sync_admin,
            edc_sync_app_config=app_config,
            edc_sync_files_app_config=django_apps.get_app_config(
                'edc_sync_files'),
            edc_sync_role=self.role,
            cors_origin_whitelist=self.cors_origin_whitelist,
            hostname=socket.gethostname(),
            ip_address=django_apps.get_app_config(
                'edc_sync_files').remote_host,
            recent_sent_tx=self.tx_exporter.history_model.objects.filter(
                sent=True).order_by('-created')[:20],
            site_models=site_sync_models.site_models,
            base_template_name=app_config.base_template_name)
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context.update({
            'pending_files': self.pending_files})
        if request.is_ajax():
            response_data = {}
            try:
                self.transaction_file_sender().file_connector.connected()
            except (ConnectionRefusedError, AuthenticationException,
                    BadHostKeyException, ConnectionResetError, SSHException,
                    OSError)as e:
                response_data = dict(
                    error=True, messages=f'An error occurred. Got {e}')
            else:
                if request.GET.get('action') == 'export_file':
                    response_data = self.export_batch()
                elif request.GET.get('action') == 'send_file':
                    response_data = self.send_file(
                        filename=request.GET.get('filename'))
                elif request.GET.get('action') == 'progress':
                    response_data = dict(
                        error=False,
                        progress=self.tx_file_sender.progress)
                elif request.GET.get('action') == 'confirm':
                    files = request.GET.get('files')
                    for filename in (files or []).split(','):
                        self.confirm_batch(filename=filename)
                elif request.GET.get('action') == 'pending_files':
                    response_data = dict(
                        pendingFiles=self.pending_files,
                        error=False)

            return HttpResponse(json.dumps(response_data),
                                content_type='application/json')
        return self.render_to_response(context)

    def send_file(self, filename=None):
        """Returns response data after sending the file.
        """
        tx_file_sender = TransactionFileSender(filename=filename)
        try:
            tx_file_sender.send()
        except IOError as e:
            response_data = dict(
                error=True,
                messages=f'Unable to send file. Got {e}')
        else:
            response_data = dict(error=False, messages='File sent.')
        return response_data

    @property
    def cors_origin_whitelist(self):
        try:
            cors_origin_whitelist = settings.CORS_ORIGIN_WHITELIST
        except AttributeError:
            cors_origin_whitelist = []
        return cors_origin_whitelist
