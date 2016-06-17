from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.views.generic import TemplateView
from example.admin import example_admin
from edc_sync.admin import edc_sync_admin

from edc_base.views.edc_base_view_mixin import EdcBaseViewMixin


class HomeView(EdcBaseViewMixin, TemplateView):
    template_name = 'example/home.html'
    app_label = 'example'

    def get_api_key(self, username):
        try:
            api_key = User.objects.get(username=username).api_key.key
        except User.DoesNotExist:
            api_key = None
        return api_key

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            example_admin=example_admin,
            edc_sync_admin=edc_sync_admin,
            api_key=self.get_api_key(self.request.user),
        )
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(HomeView, self).dispatch(*args, **kwargs)
