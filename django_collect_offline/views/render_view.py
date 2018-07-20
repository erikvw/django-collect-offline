import json

from django.apps import apps as django_apps
from django.contrib.auth.decorators import login_required
from django.core.serializers.json import Serializer
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from django_crypto_fields.constants import LOCAL_MODE
from django_crypto_fields.cryptor import Cryptor
from edc_base.view_mixins import EdcBaseViewMixin


class RenderView(EdcBaseViewMixin, TemplateView):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_template_names(self):
        return 'django_collect_offline/render_{self.kwargs.get("model_name")}.html'

    @property
    def model(self):
        model_name = self.kwargs.get('model_name')
        return django_apps.get_model('django_collect_offline', model_name)

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
