import requests
import json
from django.apps import apps as django_apps
from django.contrib.auth.models import User
from django.views.generic.base import TemplateView
from django_crypto_fields.cryptor import Cryptor
from django_crypto_fields.constants import LOCAL_MODE
from edc_base.views.edc_base_view_mixin import EdcBaseViewMixin
from django.core.serializers.json import Serializer
from django.core.exceptions import ObjectDoesNotExist
from requests.exceptions import RequestException

from edc_sync.models.host import Client, Server
from json.decoder import JSONDecodeError
from edc_sync.constants import SERVER, CLIENT


class EdcSyncViewMixin:

    @property
    def role(self):
        edc_sync_app = django_apps.get_app_config('edc_sync')
        return edc_sync_app.role

    @property
    def host_model(self):
        if self.role == SERVER:
            host_model = Client
        if self.role == CLIENT:
            host_model = Server
        return host_model

    @property
    def resource(self):
        if self.role == SERVER:
            resource = 'outgoingtransaction'
        if self.role == CLIENT:
            resource = 'incomingtransaction'
        return resource

    @property
    def hosts(self):
        hosts = {}
        for host in self.host_model.objects.filter(is_active=True):
            try:
                url = '{url}?format=json'.format(url=host.url)
                r = requests.get(url)
                list_endpoint = r.json().get(self.resource).get('list_endpoint')
                hosts.update({str(host): list_endpoint})
            except RequestException:
                pass
            except JSONDecodeError:
                pass
        return hosts

    def get_api_key(self, username):
        try:
            api_key = User.objects.get(username=username).api_key.key
        except (User.DoesNotExist, ObjectDoesNotExist):
            api_key = None
        return api_key

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            api_key=self.get_api_key(self.request.user),
            hosts=json.dumps(self.hosts),
            resource=self.resource,
        )
        return context


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
