from django.conf.urls import url, include
from tastypie.api import Api
from rest_framework.routers import DefaultRouter
from edc_sync.api.resource import OutgoingTransactionResource, IncomingTransactionResource
from edc_sync import views
from rest_framework.authtoken.views import obtain_auth_token
from django_js_reverse.views import urls_js

# v1_api = Api(api_name='v1')
# v1_api.register(OutgoingTransactionResource())
# v1_api.register(IncomingTransactionResource())

router = DefaultRouter()
router.register(r'outgoingtransaction', views.OutgoingTransactionViewSet)
router.register(r'incomingtransaction', views.IncomingTransactionViewSet)

urlpatterns = [
    url(r'^api/', include(router.urls)),
    # url(r'^tastypie/', include(v1_api.urls)),
    url(r'render/(?P<model_name>\w+)/(?P<pk>[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12})/',
        views.RenderView.as_view(), name='render_url'),
    url(r'^jsreverse/$', urls_js, name='js_reverse'),
]

urlpatterns += [
    url(r'^api-token-auth/', obtain_auth_token)
]
