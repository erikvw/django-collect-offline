from django.conf.urls import url

from rest_framework.urlpatterns import format_suffix_patterns

from edc_sync import views

urlpatterns = [
    url(r'^outgoing-transactions/$', views.OutgoingTransactionList.as_view(), name='outgoing-transaction-list'),
    url(r'^outgoing-transactions/(?P<pk>[0-9]+)/$', views.OutgoingTransactionDetail.as_view(),
        name='outgoing-transaction'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
