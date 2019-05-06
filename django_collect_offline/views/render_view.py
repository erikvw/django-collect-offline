import json

from django.apps import apps as django_apps
from django.core.serializers.json import Serializer
from django.views.generic.base import TemplateView
from django_crypto_fields.constants import LOCAL_MODE
from django_crypto_fields.cryptor import Cryptor
from edc_dashboard.view_mixins import EdcViewMixin


class RenderView(EdcViewMixin, TemplateView):
    def get_template_names(self):
        return f'django_collect_offline/render_{self.kwargs.get("model_name")}.html'

    def get_context_data(self, **kwargs):
        context = super(RenderView, self).get_context_data(**kwargs)
        context.update(json_tx=self.json_tx[0])
        context.update(json_obj=self.json_obj[0])
        return context

    @property
    def json_tx(self):
        cryptor = Cryptor()
        return json.loads(
            cryptor.aes_decrypt(self.queryset.first().tx, mode=LOCAL_MODE)
        )

    @property
    def json_obj(self):
        serializer = Serializer()
        return json.loads(
            serializer.serialize(self.queryset, use_natural_primary_keys=False)
        )

    #     @property
    #     def model_cls(self):
    #         model_name = self.kwargs.get("model_name")
    #         return django_apps.get_model("django_collect_offline", model_name)

    @property
    def queryset(self):
        model_cls = django_apps.get_model(
            "django_collect_offline", self.kwargs.get("model_name")
        )
        return model_cls.objects.filter(pk=self.kwargs.get("pk"))
