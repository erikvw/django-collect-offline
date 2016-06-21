import json

from django.apps import apps as django_apps
from json.decoder import JSONDecodeError
from requests.exceptions import RequestException

from edc_sync.constants import SERVER, CLIENT
from edc_sync.models.host import Client, Server
from rest_framework.authtoken.models import Token


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
                hosts.update({str(host): self.resource})
            except RequestException:
                pass
            except JSONDecodeError:
                pass
        return hosts

    def get_api_token(self, username):
        try:
            api_token = Token.objects.get(user__username=username).key
        except (Token.DoesNotExist):
            api_token = None
        return api_token

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            api_token=self.get_api_token(self.request.user),
            hosts=json.dumps(self.hosts),
            resource=self.resource,
        )
        return context
