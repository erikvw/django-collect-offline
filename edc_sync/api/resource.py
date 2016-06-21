from base64 import b64decode, b64encode

from django.utils.encoding import (force_bytes)
from django.utils import six

from tastypie.constants import ALL
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import DjangoAuthorization, Authorization
from tastypie.resources import ModelResource as BaseModelResource
from tastypie.serializers import Serializer
from tastypie.paginator import Paginator
from tastypie import fields

from ..models import OutgoingTransaction, IncomingTransaction
from tastypie.fields import ApiField


class BinaryField(ApiField):
    """
    A dictionary field.
    """
    dehydrated_type = 'binary'
    help_text = ""

#     def convert(self, value):
#         if value is None:
#             return None
#         return value

    def dehydrate(self, bundle, for_list=True):
        value = getattr(bundle.obj, self.attribute)
        return b64encode(force_bytes(value)).decode('ascii')

    def hydrate(self, bundle, for_list=True):
        value = getattr(bundle.obj, self.attribute)
        return six.memoryview(b64decode(force_bytes(value)))


class ModelResource(BaseModelResource):

    def alter_deserialized_list_data(self, request, data):
        data = super(ModelResource, self).alter_deserialized_list_data(request, data)
        print(data)
        return data

    @classmethod
    def api_field_from_django_field(cls, f, default=fields.CharField):
        internal_type = f.get_internal_type()
        if internal_type == 'BinaryField':
            result = BinaryField
        else:
            result = super(ModelResource, cls).api_field_from_django_field(f, default)
        return result


class OutgoingTransactionResource(ModelResource):

    class Meta:
        queryset = OutgoingTransaction.objects.filter(
            is_consumed_server=False).order_by('timestamp')
        resource_name = 'outgoingtransaction'
        authentication = ApiKeyAuthentication()
        authorization = DjangoAuthorization()
        allowed_methods = ['get', 'post', 'put', 'patch']
        always_return_data = True
#         filtering = {
#             'is_consumed_middleman': ALL,
#         }
        serializer = Serializer(formats=['json', 'xml'])
        paginator = Paginator


class IncomingTransactionResource(ModelResource):

    class Meta:
        queryset = IncomingTransaction.objects.filter(
            is_consumed=False).order_by('timestamp')
        resource_name = 'incomingtransaction'
        authentication = ApiKeyAuthentication()
        authorization = DjangoAuthorization()
        always_return_data = True
        allowed_methods = ['get', 'put', 'post', 'patch']
#         filtering = {
#             'is_consumed_middleman': ALL,
#         }
        serializer = Serializer(formats=['json', 'xml'])
        paginator = Paginator
