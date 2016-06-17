from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from edc_base.views.edc_base_view_mixin import EdcBaseViewMixin
from edc_sync.admin import edc_sync_admin
from edc_sync.views import EdcSyncViewMixin

from example.admin import example_admin


class HomeView(EdcBaseViewMixin, EdcSyncViewMixin, TemplateView):
    template_name = 'example/home.html'
    app_label = 'example'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            example_admin=example_admin,
            edc_sync_admin=edc_sync_admin,
        )
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(HomeView, self).dispatch(*args, **kwargs)
