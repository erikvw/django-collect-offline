import json
import os
import socket

from django.apps import apps as django_apps
from django.conf import settings

from django.contrib.auth.decorators import login_required
from django.core.serializers.json import Serializer
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from django_crypto_fields.constants import LOCAL_MODE
from django_crypto_fields.cryptor import Cryptor

from hurry.filesize import size

from rest_framework import status
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes)
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from edc_base.view_mixins import EdcBaseViewMixin
from edc_sync_files.transaction import TransactionExporter

from edc_sync_files.models import ExportedTransactionFileHistory

from ..admin import edc_sync_admin
from ..edc_sync_view_mixin import EdcSyncViewMixin
from ..models import (
    OutgoingTransaction, IncomingTransaction, SyncConfirmation)
from ..serializers import (
    OutgoingTransactionSerializer, IncomingTransactionSerializer,
    SyncConfirmationSerializer)
from ..site_sync_models import site_sync_models

from paramiko.ssh_exception import (
    BadHostKeyException, AuthenticationException, SSHException)
from edc_sync_files.file_transfer.send_transaction_file import TransactionFileSender


@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def api_root(request, format=None):
    return Response({
        'outgoingtransaction': reverse('outgoingtransaction-list',
                                       request=request, format=format),
        'incomingtransaction': reverse('outgoingtransaction-list',
                                       request=request, format=format),
    })


class SyncConfirmationViewSet(viewsets.ModelViewSet):
    queryset = SyncConfirmation.objects.all()
    serializer_class = SyncConfirmationSerializer

#     def perform_update(self, serializer):
#         user_instance = serializer.instance
#         request = self.request
#         serializer.save(**modified_attrs)
#         return Response(status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        return viewsets.ModelViewSet.create(self, request, *args, **kwargs)


class OutgoingTransactionViewSet(viewsets.ModelViewSet):

    queryset = OutgoingTransaction.objects.all()
    serializer_class = OutgoingTransactionSerializer

    def filter_queryset(self, queryset):
        return self.queryset.filter(
            is_consumed_server=False).order_by('timestamp')


class IncomingTransactionViewSet(viewsets.ModelViewSet):

    queryset = IncomingTransaction.objects.all()
    serializer_class = IncomingTransactionSerializer

    def filter_queryset(self, queryset):
        return self.queryset.filter(
            is_consumed=False, is_ignored=False).order_by('timestamp')


class TransactionCountView(APIView):
    """
    A view that returns the count  of transactions.
    """
    renderer_classes = (JSONRenderer,)

    def get(self, request):
        outgoingtransaction_count = OutgoingTransaction.objects.filter(
            is_consumed_server=False).count()
        outgoingtransaction_middleman_count = OutgoingTransaction.objects.filter(
            is_consumed_server=False,
            is_consumed_middleman=False).count()
        incomingtransaction_count = IncomingTransaction.objects.filter(
            is_consumed=False, is_ignored=False).count()
        content = {'outgoingtransaction_count': outgoingtransaction_count,
                   'outgoingtransaction_middleman_count': outgoingtransaction_middleman_count,
                   'incomingtransaction_count': incomingtransaction_count,
                   'hostname': socket.gethostname()}
        return Response(content, status=status.HTTP_200_OK)


class RenderView(EdcBaseViewMixin, TemplateView):

    def get_template_names(self):
        return 'edc_sync/render_{}.html'.format(self.kwargs.get('model_name'))

    @property
    def model(self):
        model_name = self.kwargs.get('model_name')
        return django_apps.get_model('edc_sync', model_name)

    @property
    def queryset(self):
        pk = self.kwargs.get('pk')
        return self.model.objects.filter(pk=pk)

    @property
    def json_tx(self):
        cryptor = Cryptor()
        return json.loads(cryptor.aes_decrypt(
            self.queryset.first().tx, mode=LOCAL_MODE))

    @property
    def json_obj(self):
        serializer = Serializer()
        return json.loads(serializer.serialize(
            self.queryset, use_natural_primary_keys=False))

    def get_context_data(self, **kwargs):
        context = super(RenderView, self).get_context_data(**kwargs)
        context.update(json_tx=self.json_tx[0])
        context.update(json_obj=self.json_obj[0])
        return context


class HomeView(EdcBaseViewMixin, EdcSyncViewMixin, TemplateView):

    template_name = 'edc_sync/home.html'
    transaction_file_sender = TransactionFileSender()

    @property
    def pending_files(self):
        """ Returns a dictionary of unsent files.
        """
        source_folder = django_apps.get_app_config(
            'edc_sync_files').source_folder
        file_attrs = []
        for history in ExportedTransactionFileHistory.objects.filter(
                sent=False).order_by('created'):
            source_filename = os.path.join(
                source_folder, history.filename)
            file_attr = os.stat(source_filename)
            data = dict({
                'filename': history.filename,
                'filesize': size(file_attr.st_size)})
            file_attrs.append(data)
        return file_attrs

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def recent_sent_transactions(self):
        return ExportedTransactionFileHistory.objects.filter(
            sent=True).order_by('-created')[:20]

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
            ip_address=self.ip_address,
            recent_sent_tx=self.recent_sent_transactions(),
            site_models=site_sync_models.site_models,
            base_template_name=app_config.base_template_name)
        return context

    @property
    def ip_address(self):
        return django_apps.get_app_config('edc_sync_files').remote_host

    @property
    def cors_origin_whitelist(self):
        try:
            cors_origin_whitelist = settings.CORS_ORIGIN_WHITELIST
        except AttributeError:
            cors_origin_whitelist = []
        return cors_origin_whitelist

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context.update({
            'pending_files': self.pending_files})
        if request.is_ajax():
            response_data = {}
            try:
                self.transaction_file_sender.file_connector.connected()
            except (ConnectionRefusedError, AuthenticationException,
                    BadHostKeyException, ConnectionResetError, SSHException,
                    OSError)as e:
                response_data = dict(
                    error=True, messages=f'An error occurred. Got {e}')
            else:
                if request.GET.get('action') == 'export_file':
                    response_data = self.export_transactions()
                elif request.GET.get('action') == 'send_file':
                    response_data = self.send_file(
                        filename=request.GET.get('filename'))
                elif request.GET.get('action') == 'progress':
                    response_data = dict(
                        error=False,
                        progress=self.transaction_file_sender.progress)
                elif request.GET.get('action') == 'confirm':
                    files = request.GET.get('files')
                    if files:
                        for filename in files.split(','):
                            self.confirm(filename)
                elif request.GET.get('action') == 'pending_files':
                    response_data = dict(
                        pendingFiles=self.pending_files,
                        error=False)

            return HttpResponse(json.dumps(response_data),
                                content_type='application/json')
        return self.render_to_response(context)

    def export_transactions(self):
        """Returns response data after exporting transactions.
        """
        source_folder = django_apps.get_app_config(
            'edc_sync_files').source_folder
        tx_exporter = TransactionExporter(source_folder)
        if tx_exporter.export_batch():
            response_data = dict(
                error=False,
                transactionFiles=self.pending_files)
        else:
            message = 'No pending data.'
            if tx_exporter.history_model.objects.filter(
                    sent=False).exists():
                message = 'Pending files found. Transfer pending files.'
            response_data = dict(messages=message, error=True)
        return response_data

    def send_file(self, filename=None):
        """Returns response data after sending the file.
        """
        transaction_file_sender = TransactionFileSender(filename=filename)
        try:
            transaction_file_sender.send()
        except IOError as e:
            response_data = dict(
                error=True,
                messages=f'Unable to send file. Got {e}')
        else:
            response_data = dict(error=False, messages='File sent.')
        return response_data

    def confirm(self, filename):
        """ Update history record after all files sent to the server.
        """
        device_id = django_apps.get_app_config('edc_device').device_id
        self.confirmation_code = (
            f'{device_id}{str(get_utcnow().strftime("%Y%m%d%H%M"))}')
        obj = self.history_model.objects.get(filename=filename)
        obj.confirmation_code = self.confirmation_code
        obj.save()
