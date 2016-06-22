from django.conf.urls import url, include
from django_js_reverse.views import urls_js
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from edc_sync import views

router = DefaultRouter()
router.register(r'outgoingtransaction', views.OutgoingTransactionViewSet)
router.register(r'incomingtransaction', views.IncomingTransactionViewSet)

urlpatterns = [
    url(r'^api/', include(router.urls)),
    url(r'render/(?P<model_name>\w+)/(?P<pk>[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12})/',
        views.RenderView.as_view(), name='render_url'),
    url(r'^jsreverse/$', urls_js, name='js_reverse'),
]

urlpatterns += [
    url(r'^api-token-auth/', obtain_auth_token)
]
