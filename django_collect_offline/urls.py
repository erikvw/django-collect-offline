from django.urls import path, re_path, include
from edc_constants.constants import UUID_PATTERN
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from .admin import django_collect_offline_admin
from .views import HomeView, RenderView
from .views import OutgoingTransactionViewSet, IncomingTransactionViewSet
from .views import TransactionCountView, OfflineReportView


router = DefaultRouter()
router.register(r"outgoingtransaction", OutgoingTransactionViewSet)
router.register(r"incomingtransaction", IncomingTransactionViewSet)

app_name = "django_collect_offline"

urlpatterns = [
    path("admin/", django_collect_offline_admin.urls),
    path(
        "api/transaction-count/",
        TransactionCountView.as_view(),
        name="transaction-count",
    ),
    path("sync-report/", OfflineReportView.as_view(), name="sync-report"),
    path("api/", include(router.urls)),
    path("api-token-auth/", obtain_auth_token),
    re_path(
        f"render/(?P<model_name>\w+)/(?P<pk>{UUID_PATTERN.pattern})/",
        RenderView.as_view(),
        name="render_url",
    ),
    path("", HomeView.as_view(), name="home_url"),
]
