from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import DjangoAuthorization
from tastypie.resources import ModelResource
from tastypie.serializers import Serializer

from ..models import OutgoingTransaction, MiddleManTransaction


class OutgoingTransactionMiddleManResource(ModelResource):

    """ APi resource based on model OutgoingTransaction filtered on is_consumed_middleman=False
    and is_consumed_server=False.

    Serve all OutgoingTransaction in netbook not yet synced by the Server and any MiddleMan"""

    class Meta:
        queryset = OutgoingTransaction.objects.filter(
            is_consumed_server=False, is_consumed_middleman=False).order_by('timestamp')
        resource_name = 'outgoingtransaction'
        authentication = ApiKeyAuthentication()
        authorization = DjangoAuthorization()
        allowed_methods = ['get', 'post', 'put', ]
        filtering = {}
        serializer = Serializer()


class OutgoingTransactionServerResource(ModelResource):

    """ APi resource based on model OutgoingTransaction filtered on is_consumed_server=False.

        Serves all OutgoingTransaction in netbook not yet synced by the Server and

        Note: it doesn't matter if MiddleMan has synced them yet or not."""

    class Meta:
        queryset = OutgoingTransaction.objects.filter(is_consumed_server=False).order_by('timestamp')
        resource_name = 'outgoingtransaction'
        authentication = ApiKeyAuthentication()
        authorization = DjangoAuthorization()
        allowed_methods = ['get', 'post', 'put', ]
        filtering = {}
        serializer = Serializer()


class MiddleManTransactionResource(ModelResource):

    """ API resource based on model MiddleManTransaction filtered on is_consumed_server=False.

    For example, serves all MiddleManTransaction in the MiddleMan not yet consumed by the Server.

    Table MiddleMan is only be queried by Server, only query for transactions not yet consumed by the Server
    i.e is_consumed_server=False.
    """

    class Meta:
        queryset = MiddleManTransaction.objects.filter(is_consumed_server=False).order_by('timestamp')
        resource_name = 'middlemantransaction'
        authentication = ApiKeyAuthentication()
        authorization = DjangoAuthorization()
        allowed_methods = ['get', 'post', 'put', ]
        filtering = {}
        serializer = Serializer()


class OutgoingTransactionSiteServerResource(ModelResource):

    """ Api resource for used for pulling transactions by the Master Server from Site Servers."""

    class Meta:
        queryset = OutgoingTransaction.objects.filter(is_consumed_server=False).order_by('timestamp')
        resource_name = 'outgoingtransaction'
        authentication = ApiKeyAuthentication()
        authorization = DjangoAuthorization()
        allowed_methods = ['get', 'post', 'put', ]
        filtering = {
        }
        serializer = Serializer()
