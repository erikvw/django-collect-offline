import os
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
from datetime import datetime

from rest_framework.generics import CreateAPIView
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from edc_base.views.edc_base_view_mixin import EdcBaseViewMixin
from edc_sync.admin import edc_sync_admin
from edc_sync.edc_sync_view_mixin import EdcSyncViewMixin
from edc_sync.models import OutgoingTransaction, IncomingTransaction, History
from edc_sync.serializers import OutgoingTransactionSerializer, IncomingTransactionSerializer, HistorySerializer
from edc_sync.classes.file_transfer import FileTransfer


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


class HistoryCreateView(CreateAPIView):

    queryset = History.objects.all()
    serializer_class = HistorySerializer

    def perform_create(self, serializer):
        serializer.save(user_created=self.request.user)


class MediaFilesAPIView(APIView):
    """
    A view that returns the count  of transactions.
    """
    renderer_classes = (JSONRenderer, )

    def get(self, request, format=None):
        return Response(json.dumps(FileTransfer().pending_media_files()))


class HomeView(EdcBaseViewMixin, EdcSyncViewMixin, TemplateView):

    template_name = 'edc_sync/home.html'

    def __init__(self, *args, **kwargs):
        super(HomeView, self).__init__(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            edc_sync_admin=edc_sync_admin,
            project_name=context.get('project_name') + ': ' + self.role.title(),
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


class PullMediaFileView(EdcBaseViewMixin, EdcSyncViewMixin, TemplateView):

    template_name = 'edc_sync/home.html'
    COMMUNITY = None
    transfer = None

    def __init__(self, *args, **kwargs):
        super(PullMediaFileView, self).__init__(*args, **kwargs)

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

    def copy_media_file(self, host, filename):
        transfer = FileTransfer(
            file_server=host, filename=filename
        )
        return transfer.pull_media_files()

    def get(self, request, *args, **kwargs):
        result = {}
        if request.is_ajax():
            host = request.GET.get('host')
            ip_address = host[:-5] if '8000' in host else host
            print(ip_address)
            action = request.GET.get('action')
            if action == 'pull':
                filename = request.GET.get('filename')
                if self.copy_media_file(ip_address, filename):
                    result = {'filename': filename, 'host': ip_address, 'status': True}
                else:
                    result = {'filename': filename, 'host': ip_address, 'status': False}
            elif action == 'media-count':
                transfer = FileTransfer(
                    file_server=host,
                )
                result = {'mediafiles': transfer.media_files_to_copy(), 'host': host}
        return HttpResponse(json.dumps(result), content_type='application/json')
