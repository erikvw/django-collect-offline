import json
from json.decoder import JSONDecodeError

from django.apps import apps as django_apps
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist

from requests.exceptions import RequestException
from rest_framework.authtoken.models import Token

from .constants import SERVER, CLIENT, NODESERVER
from .models import Client, Server
from edc_device.constants import CENTRAL_SERVER


class EdcSyncViewMixin:

    @property
    def role(self):
        edc_device_app = django_apps.get_app_config('edc_device')
        return edc_device_app.role

    @property
    def host_model(self):
        host_model = None
        if self.role in [SERVER, CENTRAL_SERVER]:
            host_model = Server
        elif self.role in [SERVER, NODESERVER]:
            host_model = Client
        elif self.role == CLIENT:
            host_model = Server
        else:
            raise ImproperlyConfigured(
                'Project uses \'edc_sync\' but has not defined a valid role for this '
                'app instance. See AppConfig. Got {}.'.format(self.role))
        return host_model

    @property
    def resource(self):
        resource = 'outgoingtransaction'
        if self.role in [SERVER, CENTRAL_SERVER, NODESERVER]:
            resource = 'outgoingtransaction'
        elif self.role == CLIENT:
            resource = 'incomingtransaction'
        else:
            raise ImproperlyConfigured(
                'Project uses \'edc_sync\' but has not defined a valid role for this '
                'app instance. See AppConfig. Got {}.'.format(self.role))
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
        except ObjectDoesNotExist:
            api_token = None
        return api_token

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            api_token=self.get_api_token(self.request.user),
            hosts=json.dumps(self.hosts),
            edc_sync_role=self.role,
            resource=self.resource,
        )
        return context
