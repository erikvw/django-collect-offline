import json

from django.apps import apps as django_apps
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from edc_device.constants import CENTRAL_SERVER, NODE_SERVER
from json.decoder import JSONDecodeError
from requests.exceptions import RequestException
from rest_framework.authtoken.models import Token

from .constants import SERVER, CLIENT
from .models import Client, Server


class OfflineViewMixin:
    @property
    def device_role(self):
        edc_device_app = django_apps.get_app_config("edc_device")
        return edc_device_app.device_role

    @property
    def host_model(self):
        host_model = None
        if self.device_role in [SERVER, CENTRAL_SERVER]:
            host_model = Server
        elif self.device_role in [SERVER, NODE_SERVER]:
            host_model = Client
        elif self.device_role == CLIENT:
            host_model = Server
        else:
            raise ImproperlyConfigured(
                "Project uses 'django_collect_offline' but has not defined a "
                "valid device role for this "
                f"app instance. See AppConfig. Got {self.device_role}."
            )
        return host_model

    @property
    def resource(self):
        resource = "outgoingtransaction"
        if self.device_role in [SERVER, CENTRAL_SERVER, NODE_SERVER]:
            resource = "outgoingtransaction"
        elif self.device_role == CLIENT:
            resource = "incomingtransaction"
        else:
            raise ImproperlyConfigured(
                "Project uses 'django_collect_offline' but has "
                f"not defined a valid role for this "
                f"app instance. See AppConfig. Got {self.device_role}."
            )
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
            django_collect_offline_role=self.device_role,
            resource=self.resource,
        )
        return context
