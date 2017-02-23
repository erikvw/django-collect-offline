from django.contrib import admin
from django.conf.urls import url, include
from django.views.generic.base import RedirectView
from django_js_reverse.views import urls_js
from edc_sync.admin import edc_sync_admin

from example.admin import example_admin
from example.views import HomeView

urlpatterns = [
    url(r'^edc_sync/', include('edc_sync.urls')),
    url(r'^admin/$', RedirectView.as_view(url='/'), name='settings_url'),
    url(r'^admin/example/', example_admin.urls),
    url(r'^admin/edc_sync/', edc_sync_admin.urls),
    url(r'^admin/django-admin/', admin.site.urls),
    url(r'home/', HomeView.as_view(), name='home_url'),
    url(r'^jsreverse/$', urls_js, name='js_reverse'),
    url(r'', include('edc_base.urls')),
]
