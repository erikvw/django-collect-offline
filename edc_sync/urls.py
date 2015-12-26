from django.conf.urls import patterns, url, include

from .api import (OutgoingTransactionMiddleManResource, OutgoingTransactionServerResource,
                  MiddleManTransactionResource, OutgoingTransactionSiteServerResource)
from .views import (index, view_transaction, consume_transactions,
                    export_outgoing_to_file, consume_from_usb)

outgoing_transaction_middle_man_resource = OutgoingTransactionMiddleManResource()
outgoing_transaction_server_resource = OutgoingTransactionServerResource()
outgoing_transaction_site_server_resource = OutgoingTransactionSiteServerResource()
middle_man_transaction_resource = MiddleManTransactionResource()

urlpatterns = patterns('',
    (r'^api_otmr/', include(outgoing_transaction_middle_man_resource.urls)),
    (r'^api_otsr/', include(outgoing_transaction_server_resource.urls)),
    (r'^api_otssr/', include(outgoing_transaction_site_server_resource.urls)),
    (r'^api_mmtr/', include(middle_man_transaction_resource.urls)),
    )

# The order is important, referred to from sync.urls and {app_name}_dispatch.urls
urlpatterns += patterns('',
    url(r'^usb_consume/(?P<app_name>[a-z0-9\-\_\.]+)/', consume_from_usb,),
    url(r'^export_outgoing/', export_outgoing_to_file, name='sync_export_outgoing_url'),
    url(r'^consume/(?P<producer>[a-z0-9\-\_\.]+)/(?P<app_name>[a-zA-Z\-\_\.]+)/', consume_transactions, name='sync_consume_producer_url'),
    url(r'^consume/(?P<producer>[a-z0-9\-\_\.]+)/', consume_transactions, name='sync_consume_producer_url'),
    url(r'^view/(?P<app_label>\w+)/(?P<model_name>\w+)/(?P<pk>[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12})/',
        view_transaction, name='view_transaction_url',),
    url(r'^view/(?P<model_name>\w+)/(?P<pk>[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12})/',
        view_transaction, name='view_transaction_url',),
    url(r'^consumed/(?P<selected_producer>[a-z0-9\-\_\.]+)/', index, name='sync_consumed'),
    url(r'^$', index, name='sync_index_url'),
    )
