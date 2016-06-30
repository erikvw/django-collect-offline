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



@api_view(['GET'])
@authentication_classes((TokenAuthentication, ))
@permission_classes((IsAuthenticated,))
def api_root(request, format=None):
    return Response({
        'outgoingtransaction': reverse('outgoingtransaction-list', request=request, format=format),
        'incomingtransaction': reverse('outgoingtransaction-list', request=request, format=format)
    })


class OutgoingTransactionViewSet(viewsets.ModelViewSet):

    queryset = OutgoingTransaction.objects.all()
    serializer_class = OutgoingTransactionSerializer

    def filter_queryset(self, queryset):
        return self.queryset.filter(is_consumed_server=False)


class IncomingTransactionViewSet(viewsets.ModelViewSet):

    queryset = IncomingTransaction.objects.all()
    serializer_class = IncomingTransactionSerializer


# class OutgoingTransactionCountView(viewsets.ModelViewSet):
#
#     queryset = OutgoingTransaction.objects.all()
#     serializer_class = OutgoingTransactionSerializer
#
#     def filter_queryset(self, queryset):
#         return self.queryset.filter(is_consumed_server=False)
#
#     def get_queryset(self):
#         return self.filter_queryset.annotate(
#             is_consumed_server=Count('is_consumed_server'),
#         )


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
        return [l for l in (
            [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2]
                if not ip.startswith("127.")][:1], [[
                    (s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close())
                    for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]
        ) if l][0][0]

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
