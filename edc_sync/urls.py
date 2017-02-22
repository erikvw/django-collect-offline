from django.conf.urls import url, include
from django_js_reverse.views import urls_js

from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from edc_sync import views
from edc_constants.constants import UUID_PATTERN
from edc_sync.admin import edc_sync_admin

router = DefaultRouter()
router.register(r'outgoingtransaction', views.OutgoingTransactionViewSet)
router.register(r'incomingtransaction', views.IncomingTransactionViewSet)

urlpatterns = [
    url(r'^admin/', edc_sync_admin.urls),
    url(r'^api/transaction-count/$',
        views.TransactionCountView.as_view(), name='transaction-count'),
    url(r'^api/', include(router.urls)),
    # url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # will reply given username and password
    url(r'^api-token-auth/', obtain_auth_token),
    # url(r'^docs/', include('rest_framework_swagger.urls')),
    url(r'render/(?P<model_name>\w+)/(?P<pk>{})/'.format(UUID_PATTERN.pattern),
        views.RenderView.as_view(), name='render_url'),
    url(r'^jsreverse/$', urls_js, name='js_reverse'),
    url(r'^', views.HomeView.as_view(), name='home_url'),
]
