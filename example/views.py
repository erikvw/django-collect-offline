import json
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from edc_base.views.edc_base_view_mixin import EdcBaseViewMixin
from edc_sync.admin import edc_sync_admin
from edc_sync.edc_sync_view_mixin import EdcSyncViewMixin
from django.http.response import HttpResponse

from example.admin import example_admin


class HomeView(EdcBaseViewMixin, EdcSyncViewMixin, TemplateView):

    template_name = 'edc_sync/home.html'
    app_label = settings.APP_LABEL

    def __init__(self, *args, **kwargs):
        super(HomeView, self).__init__(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            example_admin=example_admin,
            edc_sync_admin=edc_sync_admin,
            project_name=context.get('project_name') + ': ' + self.role.title(),
        )
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.is_ajax():
            response_data = {}
            return HttpResponse(json.dumps(response_data), content_type='application/json')
        return self.render_to_response(context)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(HomeView, self).dispatch(*args, **kwargs)
