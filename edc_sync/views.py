import json
import socket

from django.shortcuts import redirect
from django.apps import apps as django_apps
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.serializers.json import Serializer
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from django_crypto_fields.constants import LOCAL_MODE
from django_crypto_fields.cryptor import Cryptor
from django.shortcuts import render
from django.contrib import messages
from datetime import datetime

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse

from edc_base.views.edc_base_view_mixin import EdcBaseViewMixin
from edc_sync.admin import edc_sync_admin
from edc_sync.edc_sync_view_mixin import EdcSyncViewMixin
from edc_sync.models import OutgoingTransaction, IncomingTransaction
from edc_sync.serializers import OutgoingTransactionSerializer, IncomingTransactionSerializer
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from django.db.models.aggregates import Count
from edc_sync.utils.export_outgoing_transactions import export_outgoing_transactions
from edc_sync.classes.transfer_file_remotely import TransferFileRemotely


@api_view(['GET'])
@authentication_classes((TokenAuthentication, ))
@permission_classes((IsAuthenticated,))
def api_root(request, format=None):
    return Response({
        'outgoingtransaction': reverse('outgoingtransaction-list', request=request, format=format),
        'incomingtransaction': reverse('outgoingtransaction-list', request=request, format=format),
    })


class OutgoingTransactionViewSet(viewsets.ModelViewSet):

    queryset = OutgoingTransaction.objects.all()
    serializer_class = OutgoingTransactionSerializer

    def filter_queryset(self, queryset):
        return self.queryset.filter(is_consumed_server=False)


class IncomingTransactionViewSet(viewsets.ModelViewSet):

    queryset = IncomingTransaction.objects.all()
    serializer_class = IncomingTransactionSerializer


class TransactionCountView(APIView):
    """
    A view that returns the count  of transactions.
    """
    renderer_classes = (JSONRenderer, )

    def get(self, request, format=None):
        outgoingtransaction_count = OutgoingTransaction.objects.filter(is_consumed_server=False).count()
        outgoingtransaction_middleman_count = OutgoingTransaction.objects.filter(
            is_consumed_server=False,
            is_consumed_middleman=False).count()
        incomingtransaction_count = IncomingTransaction.objects.filter(is_consumed=False).count()
        content = {'outgoingtransaction_count': outgoingtransaction_count,
                   'outgoingtransaction_middleman_count': outgoingtransaction_middleman_count,
                   'incomingtransaction_count': incomingtransaction_count,
                   'hostname': socket.gethostname()}
        return Response(content)


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
        return json.loads(cryptor.aes_decrypt(self.queryset.first().tx, mode=LOCAL_MODE))

    @property
    def json_obj(self):
        serializer = Serializer()
        return json.loads(serializer.serialize(self.queryset, use_natural_primary_keys=False))

    def get_context_data(self, **kwargs):
        context = super(RenderView, self).get_context_data(**kwargs)
        context.update(json_tx=self.json_tx[0])
        context.update(json_obj=self.json_obj[0])
        return context


class HomeView(EdcBaseViewMixin, EdcSyncViewMixin, TemplateView):

    template_name = 'edc_sync/home.html'
    app_label = settings.APP_LABEL

    def __init__(self, *args, **kwargs):
        super(HomeView, self).__init__(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            edc_sync_admin=edc_sync_admin,
            project_name=self.app.verbose_name + ': ' + self.role.title(),
            cors_origin_whitelist=self.cors_origin_whitelist,
            hostname=socket.gethostname(),
            ip_address=self.ip_address,
        )
        return context

    @property
    def ip_address(self):
        return None

    @property
    def cors_origin_whitelist(self):
        try:
            cors_origin_whitelist = settings.CORS_ORIGIN_WHITELIST
        except AttributeError:
            cors_origin_whitelist = []
        return cors_origin_whitelist

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.is_ajax():
            response_data = {}
            return HttpResponse(json.dumps(response_data), content_type='application/json')
        return self.render_to_response(context)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(HomeView, self).dispatch(*args, **kwargs)


class SendTransactionFilesView(EdcBaseViewMixin, EdcSyncViewMixin, TemplateView):

    template_name = 'edc_sync/home.html'
    app_label = settings.APP_LABEL
    COMMUNITY = None

    def __init__(self, *args, **kwargs):
        super(SendTransactionFilesView, self).__init__(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            edc_sync_admin=edc_sync_admin,
            project_name=self.app.verbose_name + ': ' + self.role.title(),
            cors_origin_whitelist=self.cors_origin_whitelist,
            hostname=socket.gethostname(),
            ip_address=self.ip_address,
        )
        return context

    def get(self, request, *args, **kwargs):
        tx_count, media_count, transfer = self.files_count()
        result = dict({'media_files': media_count or 0, 'tx_files': tx_count or 0, "archived_media_no": archived})
        if request.is_ajax():
            if request.GET.get('action') == 'dump_transactions':
                if not transfer.validate_dump:
                    self.dump_transactions(self.file_name(request))
            elif request.GET.get('action') == 'transfer':
                self.transfer_transactions()
            else:
                tx_count, media_count, archived = self.files_count()
                result = dict({'media_files': media_count or 0, 'tx_files': tx_count or 0, "archived_media_no": archived})
        print("media count", media_count)
        return HttpResponse(json.dumps(result), content_type='application/json')

    def file_name(self, request):
        TODAY = datetime.today().strftime("%Y%m%d%H%M")
        file_name = "bcpp_interview_{}_{}.json".format(request.GET.get('community') or settings.COMMUNITY, TODAY)
        path = '{}{}'.format(settings.TX_DUMP_PATH, file_name)
        return path

    def files_count(self):
        transfer = TransferFileRemotely()
        media_count_dir = len(transfer.local_media_files)
        return (len(transfer.local_tx_files), media_count_dir, transfer)

    def dump_transactions(self, path):
        return export_outgoing_transactions(path)

    def transfer_transactions(self):
        transfer = TransferFileRemotely()
        transfer.send_transactions_to_server
        transfer.send_media_files_to_server
