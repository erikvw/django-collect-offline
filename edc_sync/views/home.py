import json
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
from edc_device.constants import SERVER
from edc_sync_files.classes import TransactionDumps
from edc_sync_files.classes import TransactionFileManager
from edc_sync_files.classes import transaction_messages
from edc_sync_files.models import History
from edc_sync_files.models import UploadTransactionFile

from ..admin import edc_sync_admin
from ..edc_sync_view_mixin import EdcSyncViewMixin
from ..models import OutgoingTransaction, IncomingTransaction
from ..serializers import (
    OutgoingTransactionSerializer, IncomingTransactionSerializer)
from ..site_sync_models import site_sync_models


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

    tx_file_manager = TransactionFileManager()

    def recent_sent_transactions(self):
        return History.objects.filter(
            sent=True).order_by('-created')[:20]

    def upload_transaction_files(self):
        if django_apps.get_app_config('edc_sync_files').role == SERVER:
            files = UploadTransactionFile.objects.filter(
                not_consumed__gt=0, is_played=False)
            return files
        else:
            return []
        return []

    def __init__(self, *args, **kwargs):
        super(HomeView, self).__init__(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        app_config = django_apps.get_app_config('edc_map')
        context.update(
            edc_sync_admin=edc_sync_admin,
            edc_sync_role=settings.DEVICE_ROLE,
            project_name=context.get(
                'project_name') + ': ' + self.role.title(),
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
            'pending_files': self.tx_file_manager.pending_files(),
            'upload_transaction_files': self.upload_transaction_files()})
        response_data = {
            'error': False,
            'messages': transaction_messages.messages(),
        }
        actions = [
            'dump_transaction_file', 'transfer_transaction_file',
            'get_file_transfer_progress', 'approve_files', 'pending_files']
        if request.is_ajax():
            transaction_messages.clear()
            action = request.GET.get('action') in actions
            connected = self.tx_file_manager.is_server_available() if action else False
            if connected:
                action = False
                if request.GET.get('action') == 'dump_transaction_file':
                    # dump transactions to a file
                    source_folder = django_apps.get_app_config(
                        'edc_sync_files').source_folder
                    dump = TransactionDumps(source_folder)
                    if dump.is_exported_to_json:
                        response_data.update({
                            'transactionFiles': self.tx_file_manager.file_transfer.files_dict,
                            'messages': transaction_messages.messages()
                        })
                    else:
                        response_data.update({
                            'messages': transaction_messages.messages(),
                            'error': True})
                elif request.GET.get('action') == 'transfer_transaction_file':
                    self.tx_file_manager.filename = request.GET.get('filename')
                    sent, archived = self.tx_file_manager.send_files()
                    if not (sent or archived):
                        response_data.update({
                            'messages': transaction_messages.messages(),
                            'error': True})
                elif request.GET.get('action') == 'get_file_transfer_progress':
                    response_data.update({
                        'progress': self.tx_file_manager.file_transfer_progress
                    })
                elif request.GET.get('action') == 'approve_files':
                    files = request.GET.get('files')
                    if files:
                        files = files.split(',')
                        self.tx_file_manager.approve_transfer_files(files)
                elif request.GET.get('action') == 'pending_files':
                    response_data.update({
                        'messages': transaction_messages.messages(),
                        'pendingFiles': self.tx_file_manager.pending_files(),
                        'error': False})
            else:
                host = django_apps.get_app_config(
                    'edc_sync_files').remote_host
                response_data.update({
                    'error': True,
                    'host': host,
                    'messages': transaction_messages.messages(),
                })
            return HttpResponse(json.dumps(response_data),
                                content_type='application/json')
        return self.render_to_response(context)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(HomeView, self).dispatch(*args, **kwargs)
