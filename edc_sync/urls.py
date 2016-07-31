from django.conf.urls import url, include
from django_js_reverse.views import urls_js

from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from edc_sync import views
from edc_sync.admin import edc_sync_admin

router = DefaultRouter()
router.register(r'outgoingtransaction', views.OutgoingTransactionViewSet)
router.register(r'incomingtransaction', views.IncomingTransactionViewSet)

urlpatterns = [
    url(r'^api/transaction-count/$', views.TransactionCountView.as_view(), name='transaction-count'),
    url(r'^api/', include(router.urls)),
    # url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api-token-auth/', obtain_auth_token),  # will reply given username and password
    url(r'^docs/', include('rest_framework_swagger.urls')),
    url(r'render/(?P<model_name>\w+)/(?P<pk>[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12})/',
        views.RenderView.as_view(), name='render_url'),
    url(r'^jsreverse/$', urls_js, name='js_reverse'),
    url(r'^admin/', edc_sync_admin.urls),
    url(r'^', views.HomeView.as_view(), name='edc-sync-home-url'),
]
