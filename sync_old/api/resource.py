from tastypie.serializers import Serializer
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import DjangoAuthorization
from tastypie.resources import ModelResource
from edc.device.sync.models import OutgoingTransaction, MiddleManTransaction

"""
from django.contrib.auth.models import User
from django.db import models
from tastypie.models import create_api_key
for user in User.objects.all():
    if not ApiKey.objects.filter(user=user):
        create_api_key(instance=user, created=True)

from django.contrib.auth.models import User
from django.db import models
from tastypie.models import create_api_key
for user in User.objects.filter(username__in=names):
    if not ApiKey.objects.filter(user=user):
        ApiKey.objects.create(user=user)

api_key = ApiKey.objects.get(user=User.objects.get(username='erikvw'))
api_key.key='1af87bd7d0c7763e7b11590c9398740f0de7678b'
api_key.save()

api_key = ApiKey.objects.get(user=User.objects.get(username='kbinda'))
api_key.key='0a0b09212e2661d01b09ffe2c780145dc86c1cd6'
api_key.save()

api_key = ApiKey.objects.get(user=User.objects.get(username='tlentswe'))
api_key.key='93d15e5d8b8c589c28be956a4419d18c5c657924'
api_key.save()

api_key = ApiKey.objects.get(user=User.objects.get(username='django'))
api_key.key='1af87bd7d0c7763e7b11590c9398740f0de7678b'
api_key.save()
names = ['onep','ckgathi','chick','django','erikvw','jtshikedi','rmabutho','ankhutelang', 'tbasuti', 'tmoruiemang', 'ambikiwa', 'ksebinang', 'kkeothepile', 'lmmesi', 'lramatokwane', 'nkeakantse', 'smbayi', 'tkgautlhe']

if you get <<ValueError: astimezone() cannot be applied to a naive datetime>> when trying to create ApiKeys,
replace 
def now: 
    return timezone.localtime.(timezone.now())
with
def now():
        d = timezone.now()
        if d.tzinfo:
           return timezone.localtime(timezone.now())
        return d
at python2.7/site-packages/tastypie/utils/timezone.py.
"""

class OutgoingTransactionMiddleManResource(ModelResource):

    """ APi resource based on model OutgoingTransaction filtered on is_consumed_middleman=False and is_consumed_server=False. 
        i.e Serve me all OutgoingTransaction in netbook not yet synced by the Server and any MiddleMan"""

    class Meta:
        # Table OutgoingTransanctions{in netbook} in the case that it is accessed by Middleman
        # We give transanctions that are not consumed by the Server and MiddleMan
        queryset = OutgoingTransaction.objects.filter(is_consumed_server=False, is_consumed_middleman=False).order_by('timestamp')
        resource_name = 'outgoingtransaction'
        authentication = ApiKeyAuthentication()
        authorization = DjangoAuthorization()
        allowed_methods = ['get', 'post', 'put', ]
        filtering = {
            #'producer': ['exact', ],
        }
        serializer = Serializer()
# http://localhost:8000/bhp_sync/api/outgoingtransaction/?format=json&username=django&api_key=1af87bd7d0c7763e7b11590c9398740f0de7678b
class OutgoingTransactionServerResource(ModelResource):

    """ APi resource based on model OutgoingTransaction filtered on is_consumed_server=False. 
        i.e Serve me all OutgoingTransaction in netbook not yet synced by the Server and
            we do not care if MiddleMan has synced them yet or not."""

    class Meta:
        # Table OutgoingTransanctions{in netbook} in the case that it is accessed by Server
        # We give transanctions that are not consumed by Server, we do not care whether consumed by MiddleMan or not
        queryset = OutgoingTransaction.objects.filter(is_consumed_server=False).order_by('timestamp')
        resource_name = 'outgoingtransaction'
        authentication = ApiKeyAuthentication()
        authorization = DjangoAuthorization()
        allowed_methods = ['get', 'post', 'put', ]
        filtering = {
            #'producer': ['exact', ],
        }
        serializer = Serializer()


class MiddleManTransactionResource(ModelResource):

    """ API resource based on model MiddleManTransaction filtered on is_consumed_server=False.

    For example, serves me all MiddleManTransaction in the MiddleMan not yet synced by the Server."""

    class Meta:
        # Table MiddleMan will only be queried by Server, hence we give only those transanctions not yet consumed by the Server
        # i.e is_consumed_server=False
        queryset = MiddleManTransaction.objects.filter(is_consumed_server=False).order_by('timestamp')
        resource_name = 'middlemantransaction'
        authentication = ApiKeyAuthentication()
        authorization = DjangoAuthorization()
        allowed_methods = ['get', 'post', 'put', ]
        filtering = {
#             'producer': ['exact', ],
        }
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
#            'producer': ['exact', ],
        }
        serializer = Serializer()
# models.signals.post_save.connect(create_api_key, sender=User)
